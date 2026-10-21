#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""铁路危货双重预防机制评估系统 · 一键启动前后端

双击“启动项目.bat”即可运行；也可在命令行执行：
    python 启动项目.py [--no-browser] [--no-pause]

启动流程：检查 MySQL → 停止已在运行的本项目前后端（含 --reload 工作进程与残留进程）
→ 确认端口已释放 → 重新启动后端与前端。
每次都是全新启动，避免旧进程占用端口、残留旧代码导致页面与接口不一致。
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # scripts/ 的上一级
FRONTEND_DIR = ROOT / 'frontend'
BACKEND_DIR = ROOT / 'backend'
PYTHON_EXE = BACKEND_DIR / '.venv' / 'Scripts' / 'python.exe'

BACKEND_PORT = 8000
FRONTEND_PORT = 5173
MYSQL_PORT = 3306

SERVICE_PORTS = ((BACKEND_PORT, '后端'), (FRONTEND_PORT, '前端'))
BACKEND_KEY = str(BACKEND_DIR).lower()
FRONTEND_KEY = str(FRONTEND_DIR).lower()
SELF_PID = os.getpid()

HEALTH_URL = f'http://localhost:{BACKEND_PORT}/api/health'
FRONTEND_URL = f'http://localhost:{FRONTEND_PORT}/'


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


# --------------------------------------------------------------------------- 基础探测


def local_addresses(port: int) -> list[tuple[int, tuple]]:
    """localhost 可能同时解析到 IPv4 与 IPv6，两类地址都要探测。"""
    try:
        infos = socket.getaddrinfo('localhost', port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        infos = [(socket.AF_INET, socket.SOCK_STREAM, 0, '', ('127.0.0.1', port))]
    addresses: list[tuple[int, tuple]] = []
    for family, _socktype, _proto, _canon, sockaddr in infos:
        if (family, sockaddr) not in addresses:
            addresses.append((family, sockaddr))
    return addresses


def port_open(port: int, timeout: float = 1.0) -> bool:
    for family, sockaddr in local_addresses(port):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            if sock.connect_ex(sockaddr) == 0:
                return True
    return False


def http_body(url: str, timeout: float = 3.0) -> str:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            if not 200 <= response.status < 400:
                return ''
            return response.read(6000).decode('utf-8', 'replace')
    except (urllib.error.URLError, OSError, ValueError):
        return ''


def backend_service_alive() -> bool:
    """本项目后端特征：/api/health 返回 status 与 database 字段。"""
    body = http_body(HEALTH_URL)
    return '"status"' in body and '"database"' in body


def frontend_service_alive() -> bool:
    """本项目前端特征：Vite 页面（含 @vite/client 或本项目标题/根节点）。"""
    body = http_body(FRONTEND_URL)
    if not body:
        return False
    return any(marker in body for marker in ('/@vite/client', 'id="root"', '铁路危货'))


def service_alive(kind: str) -> bool:
    return backend_service_alive() if kind == '后端' else frontend_service_alive()


def wait_until(check, seconds: float, label: str, interval: float = 1.0) -> bool:
    deadline = time.time() + seconds
    interactive = sys.stdout.isatty()
    elapsed = 0.0
    while time.time() < deadline:
        if check():
            if interactive and elapsed:
                print(' ' * 56, end='\r')
            return True
        if interactive:
            print(f'      等待{label}… {elapsed:.0f}s', end='\r')
        elif elapsed and int(elapsed) % 5 == 0:
            print(f'      等待{label}… {elapsed:.0f}s')
        time.sleep(interval)
        elapsed += interval
    if interactive:
        print(' ' * 56, end='\r')
    return check()


# --------------------------------------------------------------------------- 进程识别


def listening_pids(port: int) -> set[int]:
    """netstat 找出监听指定端口的进程号（同时覆盖 IPv4 与 IPv6）。"""
    try:
        completed = subprocess.run(
            ['netstat', '-ano', '-p', 'TCP'],
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    pids: set[int] = set()
    for line in (completed.stdout or '').splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0].upper() != 'TCP' or parts[3].upper() != 'LISTENING':
            continue
        if parts[1].endswith(f':{port}'):
            try:
                pids.add(int(parts[4]))
            except ValueError:
                continue
    return pids


def running_processes() -> dict[int, tuple[int, str, str]]:
    """读取全部进程：{进程号: (父进程号, 可执行文件路径, 命令行)}。"""
    script = (
        '[Console]::OutputEncoding=[Text.Encoding]::UTF8;'
        'Get-CimInstance Win32_Process | Where-Object { $_.CommandLine } | '
        'ForEach-Object { "{0}`t{1}`t{2}`t{3}" -f $_.ProcessId, $_.ParentProcessId, $_.ExecutablePath,'
        ' ($_.CommandLine -replace "`t", " ") }'
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = Path(tmp_dir) / 'processes.txt'
        try:
            subprocess.run(
                ['powershell', '-NoProfile', '-NonInteractive', '-Command',
                 f'{script} | Out-File -LiteralPath "{out_path}" -Encoding utf8'],
                capture_output=True, timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            return {}
        if not out_path.exists():
            return {}
        text = out_path.read_text(encoding='utf-8-sig', errors='replace')

    processes: dict[int, tuple[int, str, str]] = {}
    for line in text.splitlines():
        parts = line.split('\t')
        if len(parts) < 4:
            continue
        try:
            pid = int(parts[0].strip())
            ppid = int(parts[1].strip())
        except ValueError:
            continue
        processes[pid] = (ppid, parts[2].strip(), '\t'.join(parts[3:]).strip())
    return processes


def classify(exe_path: str, cmdline: str) -> str | None:
    """只看带项目路径特征的后端/前端进程（严格匹配，绝不误杀其它程序）。"""
    text = f'{exe_path} {cmdline}'.lower()
    if BACKEND_KEY in text and 'uvicorn' in text and 'app.main:app' in text:
        return '后端'
    if FRONTEND_KEY in text and ('vite' in text or 'npm-cli.js' in text):
        return '前端'
    return None


def is_service_launcher(cmdline: str) -> bool:
    """运行本服务的命令行窗口：cmd /k npm run dev、cmd /k ... uvicorn ...。"""
    lowered = cmdline.lower()
    if 'cmd.exe' not in lowered:
        return False
    if 'npm run dev' in lowered:
        return True
    return 'uvicorn' in lowered and 'app.main:app' in lowered


def try_stop(pid: int) -> None:
    """停止进程树：先用 taskkill，失败再用 PowerShell 兜底。
    是否真正停止以“端口是否释放”为准，这里不做成功与否的判断。"""
    try:
        subprocess.run(
            ['taskkill', '/F', '/T', '/PID', str(pid)],
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        pass
    if not port_open(BACKEND_PORT, 0.3) and not port_open(FRONTEND_PORT, 0.3):
        return
    try:
        subprocess.run(
            ['powershell', '-NoProfile', '-NonInteractive', '-Command',
             f'Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue'],
            capture_output=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        pass


# --------------------------------------------------------------------------- 停止服务


def is_project_service(exe_path: str, cmdline: str) -> bool:
    """本项目的服务进程：带项目路径的 uvicorn / vite，或运行服务的命令行窗口。"""
    if classify(exe_path, cmdline) or is_service_launcher(cmdline):
        return True
    text = f'{exe_path} {cmdline}'.lower()
    if 'python' in text and 'uvicorn' in text and 'app.main:app' in text:
        return True
    return 'node' in text and 'vite' in text and FRONTEND_KEY in text


def find_project_ancestor(pid: int, processes: dict[int, tuple[int, str, str]]) -> int | None:
    """沿父链向上找最上层的项目服务进程（uvicorn --reload 的主进程等），
    停止它即可连带停掉其派生的工作进程，避免工作进程被杀后又重生。"""
    best: int | None = None
    current = pid
    for _ in range(8):
        info = processes.get(current)
        if not info:
            break
        parent = processes.get(info[0])
        if not parent:
            break
        if is_project_service(parent[1], parent[2]):
            best = info[0]
            if is_service_launcher(parent[2]):
                break
            current = info[0]
        else:
            break
    return best


def tree_order(plan: dict[int, tuple[str, str]], processes: dict[int, tuple[int, str, str]]) -> list[int]:
    """按进程树由上层到下层排序，先停父进程再停子进程。"""
    depths: dict[int, int] = {}
    for pid in plan:
        depth = 0
        current = pid
        for _ in range(8):
            info = processes.get(current)
            if not info:
                break
            if info[0] in plan:
                depth += 1
                current = info[0]
            else:
                break
        depths[pid] = depth
    return sorted(plan, key=lambda pid: (depths.get(pid, 0), pid))


def stop_services() -> list[tuple[str, int]]:
    """停止本项目的旧服务（含 --reload 工作进程与残留进程），返回端口仍被占用的清单。"""
    print('[2/5] 旧服务              ：正在检查并停止…')
    handled: set[int] = set()

    # 反复清场：uvicorn 主进程被停前可能已派生新的工作进程，端口占用者也可能被重启
    for _round in range(6):
        processes = running_processes()
        plan: dict[int, tuple[str, str]] = {}

        def add(pid: int, kind: str, reason: str) -> None:
            if pid and pid != SELF_PID and pid not in plan:
                plan[pid] = (kind, reason)

        # 1) 命令行或可执行路径带项目特征的服务进程（uvicorn 主进程、vite 等）
        for pid, (_ppid, exe_path, cmdline) in processes.items():
            kind = classify(exe_path, cmdline)
            if kind:
                add(pid, kind, '项目进程')

        # 2) 服务端口的占用者：优先停其最上层的项目祖先进程，连带其工作进程
        for port, kind in SERVICE_PORTS:
            for pid in listening_pids(port):
                if pid == SELF_PID:
                    continue
                ancestor = find_project_ancestor(pid, processes)
                if ancestor:
                    add(ancestor, kind, f'占用端口 {port}')
                    continue
                info = processes.get(pid)
                if info and is_project_service(info[1], info[2]):
                    add(pid, kind, f'占用端口 {port}')
                elif service_alive(kind):
                    # 命令行已无从判断（--reload 子进程、短路径等），按服务特征确认后停止
                    add(pid, kind, f'占用端口 {port}（按服务特征判定）')

        pending = [pid for pid in tree_order(plan, processes) if pid not in handled]
        if not pending:
            break

        for pid in pending:
            handled.add(pid)
            kind, reason = plan[pid]
            print(f'      · 停止{kind}（PID {pid}，{reason}）')
            try_stop(pid)
        time.sleep(1.2)

    if not handled:
        print('      没有检测到正在运行的本项目前后端')

    still_busy: list[tuple[str, int]] = []
    for port, kind in SERVICE_PORTS:
        if not port_open(port, 0.3):
            continue
        still_busy.append((kind, port))
        pids = '、'.join(str(pid) for pid in sorted(listening_pids(port))) or '未知'
        print(f'      ⚠ 端口 {port} 仍被占用（PID {pids}），{kind}本次未能停止')
        if service_alive(kind):
            print('         该端口仍在提供本系统服务，可依次尝试：')
            print(f'           1) 在任务管理器中结束 PID {pids} 对应的进程；')
            print('           2) 右键“启动项目.bat”→“以管理员身份运行”；')
            print('           3) 重启电脑后再次运行本脚本。')
        else:
            print('         该端口被其它程序占用，请关闭该程序或改用其它端口后再启动')

    released = [str(port) for port, _kind in SERVICE_PORTS if all(port != busy_port for _k, busy_port in still_busy)]
    if released:
        print(f'      · 端口 {"、".join(released)} 已释放')
    return still_busy


# --------------------------------------------------------------------------- 启动服务


def start_backend() -> bool:
    if not PYTHON_EXE.exists():
        print(f'  ✗ 未找到后端虚拟环境：{PYTHON_EXE}')
        print('    请在 backend 下创建虚拟环境（python -m venv .venv）并安装 requirements.txt')
        return False
    subprocess.Popen(
        [str(PYTHON_EXE), '-m', 'uvicorn', 'app.main:app', '--reload', '--port', str(BACKEND_PORT)],
        cwd=str(BACKEND_DIR),
        creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0),
    )
    return True


def start_frontend() -> bool:
    subprocess.Popen(
        ['cmd', '/k', 'npm run dev'],
        cwd=str(FRONTEND_DIR),
        creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0),
    )
    return True


def main() -> int:
    configure_console()
    parser = argparse.ArgumentParser(description='一键启动铁路危货双重预防机制评估系统')
    parser.add_argument('--no-browser', action='store_true', help='启动完成后不自动打开浏览器')
    parser.add_argument('--no-pause', action='store_true', help='结束后不等待回车（自动化调用时使用）')
    args = parser.parse_args()

    print('=' * 62)
    print('  铁路危货双重预防机制评估系统 · 一键启动')
    print('=' * 62)
    print(f'项目目录：{ROOT}')
    print()

    # 1. 数据库
    if port_open(MYSQL_PORT):
        print(f'[1/5] MySQL（端口 {MYSQL_PORT}）      ：已运行')
    else:
        print(f'[1/5] MySQL（端口 {MYSQL_PORT}）      ：未运行 ✗')
        print('       请先启动 MySQL 服务，例如在管理员命令行执行： net start MySQL80')
        print('       若还没有数据库，请先运行“数据库初始化包\\初始化数据库.bat”')

    # 2. 先停止已经在运行的本项目前后端
    print()
    busy_ports = stop_services()

    # 3. 后端
    print()
    if any(port == BACKEND_PORT for _kind, port in busy_ports):
        print(f'[3/5] 后端（端口 {BACKEND_PORT}）        ：端口被占用，未启动 ✗')
    else:
        print(f'[3/5] 后端（端口 {BACKEND_PORT}）        ：正在启动…')
        if not start_backend():
            return 1
        if wait_until(backend_service_alive, 60, '后端就绪'):
            print(f'[3/5] 后端（端口 {BACKEND_PORT}）        ：启动成功 ✓')
        else:
            print(f'[3/5] 后端（端口 {BACKEND_PORT}）        ：启动超时 ✗')
            print('       请查看新打开的窗口里是否有报错（常见原因：MySQL 未启动、数据库未初始化、端口被占用）')

    # 4. 前端
    print()
    if any(port == FRONTEND_PORT for _kind, port in busy_ports):
        print(f'[4/5] 前端（端口 {FRONTEND_PORT}）        ：端口被占用，未启动 ✗')
    else:
        print(f'[4/5] 前端（端口 {FRONTEND_PORT}）        ：正在启动…')
        if not start_frontend():
            return 1
        if wait_until(frontend_service_alive, 90, '前端就绪'):
            print(f'[4/5] 前端（端口 {FRONTEND_PORT}）        ：启动成功 ✓')
        else:
            print(f'[4/5] 前端（端口 {FRONTEND_PORT}）        ：启动超时 ✗')
            print('       请查看新打开的窗口里是否有报错（常见原因：依赖未安装，先执行 npm install）')

    # 5. 汇总
    print()
    print('[5/5] 访问信息')
    print(f'       门户首页      ：{FRONTEND_URL}')
    print(f'       管理平台接口  ：http://localhost:{BACKEND_PORT}/docs')
    print('       登录账号      ：admin / admin123456（管理员）')
    print('       也可在登录页选择“以离线演示身份进入”（不依赖后端）')
    print()
    print('提示：新打开的两个窗口分别是前端与后端的运行日志，关闭窗口即停止对应服务。')
    print('      下次再运行本脚本时，会先停止这两个服务再重新启动。')

    if not args.no_browser:
        webbrowser.open(FRONTEND_URL)

    if not args.no_pause:
        input('\n按回车键关闭本窗口…')
    return 0


if __name__ == '__main__':
    sys.exit(main())
