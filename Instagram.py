#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Golike Automation Tool
Created by: Trần Đức Doanh
Version: 2.0 Enhanced
"""

import requests
import time
import os
import json
import random
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.text import Text
    from rich.align import Align
    from rich import box
    from rich.live import Live
    from rich.status import Status
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.layout import Layout
    from rich.syntax import Syntax
    from rich.traceback import install
except ImportError as e:
    print("🔄 Đang cài đặt thư viện cần thiết...")
    os.system("pip install requests rich")
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
        from rich.prompt import Prompt, IntPrompt, Confirm
        from rich.text import Text
        from rich.align import Align
        from rich import box
        from rich.live import Live
        from rich.status import Status
        from rich.columns import Columns
        from rich.rule import Rule
        from rich.layout import Layout
        from rich.syntax import Syntax
        from rich.traceback import install
    except ImportError:
        print("❌ Không thể cài đặt thư viện. Vui lòng chạy: pip install requests rich")
        sys.exit(1)

# Cài đặt rich traceback để hiển thị lỗi đẹp hơn
install(show_locals=True)

# Khởi tạo console với width tối ưu
console = Console(width=120, force_terminal=True)

class Colors:
    """Class chứa các màu sắc cho giao diện"""
    PRIMARY = "bold blue"
    SUCCESS = "bold green"
    WARNING = "bold yellow"
    ERROR = "bold red"
    INFO = "bold cyan"
    ACCENT = "bold magenta"
    MUTED = "dim white"

class InstagramBot:
    """Class chính để xử lý Instagram automation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {}
        self.user_info = {}
        self.account_id = None
        self.cookie_instagram = None
        
    def enhanced_countdown(self, time_sec: int, message: str = "Đang chờ") -> None:
        """Countdown với giao diện đẹp hơn"""
        with Progress(
            SpinnerColumn("dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"[cyan]{message}", total=time_sec)
            
            for remaining in range(time_sec, -1, -1):
                progress.update(
                    task, 
                    description=f"[yellow]⏱️  {message} - còn lại {remaining}s",
                    completed=time_sec-remaining
                )
                time.sleep(1)
            
            progress.update(task, description="[green]✅ Hoàn thành!", completed=time_sec)
            time.sleep(0.5)

    def create_beautiful_banner(self) -> None:
        """Tạo banner đẹp với Rich"""
        console.clear()
        
        # ASCII Art Banner
        banner_text = Text()
        ascii_art = """
    ██╗███╗   ██╗███████╗████████╗ █████╗  ██████╗ ██████╗  █████╗ ███╗   ███╗
    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
    ██║██╔██╗ ██║███████╗   ██║   ███████║██║  ███╗██████╔╝███████║██╔████╔██║
    ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
    ██║██║ ╚████║███████║   ██║   ██║  ██║╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
    ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
                             BOT AUTOMATION V2.0 ENHANCED
        """
        
        banner_text.append(ascii_art, style="bold cyan")
        
        banner_panel = Panel(
            Align.center(banner_text),
            title="[bold blue]🤖 INSTAGRAM GOLIKE AUTOMATION TOOL VIP",
            subtitle="[bold green]Enhanced by AI | Trần Đức Doanh 💎",
            border_style="blue",
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        )
        
        # Thông tin liên hệ
        contact_columns = Columns([
            Panel(
                "[bold cyan]📱 Telegram\n[white]@doanhvip1",
                border_style="cyan",
                box=box.ROUNDED,
                width=25
            ),
            Panel(
                "[bold red]🎵 TikTok\n[white]@doanh21105",
                border_style="red", 
                box=box.ROUNDED,
                width=25
            ),
            Panel(
                "[bold yellow]👑 Version\n[white]2.0 Enhanced",
                border_style="yellow",
                box=box.ROUNDED,
                width=25
            ),
            Panel(
                "[bold green]💎 Status\n[white]VIP Premium",
                border_style="green",
                box=box.ROUNDED,
                width=25
            )
        ], equal=True)
        
        console.print(banner_panel)
        console.print()
        console.print(contact_columns)
        console.print()

    def validate_auth_token(self, token: str) -> bool:
        """Kiểm tra tính hợp lệ của auth token"""
        if not token or len(token) < 10:
            return False
        
        test_headers = {
            'Authorization': token,
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        try:
            response = self.session.get(
                'https://gateway.golike.net/api/users/me',
                headers=test_headers,
                timeout=10
            )
            return response.status_code == 200 and response.json().get('status') == 200
        except:
            return False

    def get_instagram_accounts(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tài khoản Instagram"""
        try:
            url = 'https://gateway.golike.net/api/instagram-account'
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    return data.get('data', [])
            return []
        except Exception as e:
            console.print(f"[{Colors.ERROR}]❌ Lỗi khi lấy danh sách Instagram: {str(e)}")
            return []

    def display_instagram_accounts(self, accounts: List[Dict[str, Any]]) -> Optional[int]:
        """Hiển thị danh sách tài khoản Instagram và cho phép chọn"""
        if not accounts:
            console.print(Panel(
                "[bold red]❌ Không tìm thấy tài khoản Instagram nào!\n"
                "[yellow]Vui lòng thêm tài khoản Instagram vào Golike trước.",
                title="[bold red]🚫 KHÔNG CÓ TÀI KHOẢN",
                border_style="red"
            ))
            return None
        
        # Tạo bảng hiển thị tài khoản
        table = Table(
            title="[bold cyan]📱 DANH SÁCH TÀI KHOẢN INSTAGRAM",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold blue"
        )
        
        table.add_column("[bold blue]STT", style="cyan", no_wrap=True, width=8)
        table.add_column("[bold green]👤 Username", style="green", width=25)
        table.add_column("[bold yellow]📊 Trạng thái", style="yellow", width=15)
        table.add_column("[bold magenta]📱 Followers", style="magenta", width=15)
        table.add_column("[bold cyan]🔗 ID", style="cyan", width=15)
        
        for i, account in enumerate(accounts, 1):
            username = account.get('instagram_username', 'N/A')
            account_id = account.get('id', 'N/A')
            status = "[green]✅ Hoạt động" if account.get('status') == 'active' else "[red]❌ Tạm khóa"
            followers = account.get('followers', 'N/A')
            
            table.add_row(
                str(i),
                f"[bold cyan]@{username}",
                status,
                str(followers) if isinstance(followers, int) else str(followers),
                str(account_id)
            )
        
        console.print(table)
        console.print()
        
        try:
            choice = IntPrompt.ask(
                "[bold yellow]🎯 Chọn tài khoản Instagram (nhập số thứ tự)",
                default=1,
                choices=[str(i) for i in range(1, len(accounts) + 1)]
            )
            return choice - 1
        except KeyboardInterrupt:
            console.print("\n[bold red]❌ Đã hủy thao tác!")
            return None

    def get_instagram_cookie(self, account_id: str) -> Optional[str]:
        """Lấy hoặc nhập cookie Instagram"""
        cookie_file = f'COOKIEINS{account_id}.txt'
        
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie = f.read().strip()
                    if cookie:
                        console.print(f"[{Colors.SUCCESS}]✅ Đã tìm thấy cookie cho tài khoản!")
                        return cookie
            except Exception as e:
                console.print(f"[{Colors.WARNING}]⚠️  Lỗi đọc file cookie: {str(e)}")
        
        # Nếu không có cookie, yêu cầu nhập
        console.print(Panel(
            "[bold yellow]🍪 NHẬP COOKIE INSTAGRAM\n\n"
            "[white]Hướng dẫn lấy cookie:\n"
            "[cyan]1. Mở Instagram.com trên trình duyệt\n"
            "[cyan]2. Đăng nhập tài khoản của bạn\n"
            "[cyan]3. Nhấn F12 → Application/Storage → Cookies\n"
            "[cyan]4. Copy toàn bộ cookie và paste vào đây",
            title="[bold green]📋 HƯỚNG DẪN",
            border_style="yellow"
        ))
        
        try:
            cookie = Prompt.ask("[bold green]🍪 Nhập Cookie Instagram", password=True)
            if cookie:
                with open(cookie_file, 'w', encoding='utf-8') as f:
                    f.write(cookie)
                console.print(f"[{Colors.SUCCESS}]✅ Đã lưu cookie thành công!")
                return cookie
            else:
                console.print(f"[{Colors.ERROR}]❌ Cookie không được để trống!")
                return None
        except KeyboardInterrupt:
            console.print("\n[bold red]❌ Đã hủy thao tác!")
            return None

    def create_instagram_headers(self, cookie: str) -> Dict[str, str]:
        """Tạo headers cho Instagram API"""
        try:
            csrf_token = cookie.split('csrftoken=')[1].split(';')[0]
        except (IndexError, AttributeError):
            console.print(f"[{Colors.ERROR}]❌ Cookie không hợp lệ! Không tìm thấy csrftoken.")
            return {}
        
        return {
            'accept': '*/*',
            'accept-language': 'vi,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': cookie,
            'origin': 'https://www.instagram.com',
            'priority': 'u=1, i',
            'referer': 'https://www.instagram.com/',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-asbd-id': '129477',
            'x-csrftoken': csrf_token,
            'x-ig-app-id': '936619743392459',
            'x-instagram-ajax': '1014868636',
            'x-requested-with': 'XMLHttpRequest',
        }
    def get_job_configuration(self) -> tuple[int, int]:
        """Lấy cấu hình số lượng job và delay"""
        console.print(Panel(
            "[bold cyan]⚙️  CẤU HÌNH TOOL\n\n"
            "[yellow]📊 Số lượng job: Số nhiệm vụ muốn thực hiện\n"
            "[yellow]⏱️  Delay: Thời gian nghỉ giữa các job (giây)\n"
            "[yellow]💡 Khuyến nghị: 10-30 giây để tránh spam",
            title="[bold green]📋 HƯỚNG DẪN CẤU HÌNH",
            border_style="green"
        ))
        
        try:
            num_jobs = IntPrompt.ask(
                "[bold cyan]🎯 Nhập số lượng Job muốn làm",
                default=50,
                choices=list(map(str, range(1, 1001)))
            )
            
            delay = IntPrompt.ask(
                "[bold yellow]⏱️  Nhập Delay giữa các job (giây)",
                default=15,
                choices=list(map(str, range(5, 121)))
            )
            
            return num_jobs, delay
        except KeyboardInterrupt:
            console.print("\n[bold red]❌ Đã hủy cấu hình!")
            return 0, 0

    def perform_instagram_action(self, job_data: Dict[str, Any], instagram_headers: Dict[str, str]) -> bool:
        """Thực hiện hành động Instagram (follow/like)"""
        job_type = job_data.get('type')
        object_id = job_data.get('object_id')
        
        if job_type == 'follow':
            url = f'https://www.instagram.com/api/v1/friendships/create/{object_id}/'
            data = {
                'container_module': 'profile',
                'nav_chain': 'PolarisFeedRoot:feedPage:8:topnav-link',
                'user_id': object_id,
            }
            
            try:
                response = requests.post(url, headers=instagram_headers, data=data, timeout=15)
                response_text = response.text
                
                if '"status":"ok"' in response_text:
                    return True
                elif '"spam":true' in response_text:
                    console.print(f"[{Colors.WARNING}]🚫 Tài khoản bị chặn Follow")
                    return False
                elif '"require_login":true' in response_text:
                    console.print(f'[{Colors.ERROR}]💀 Cookie đã hết hạn!')
                    # Xóa file cookie cũ
                    cookie_file = f'COOKIEINS{self.account_id}.txt'
                    if os.path.exists(cookie_file):
                        os.remove(cookie_file)
                    return False
                else:
                    return False
                    
            except Exception as e:
                console.print(f"[{Colors.ERROR}]❌ Lỗi follow: {str(e)}")
                return False
                
        elif job_type == 'like':
            like_id = job_data.get('description')
            url = f'https://www.instagram.com/api/v1/web/likes/{like_id}/like/'
            
            try:
                response = requests.post(url, headers=instagram_headers, timeout=15)
                response_text = response.text
                
                if '"status":"ok"' in response_text:
                    return True
                elif '"spam":true' in response_text:
                    console.print(f"[{Colors.WARNING}]🚫 Tài khoản bị chặn Like")
                    return False
                elif '"require_login":true' in response_text:
                    console.print(f'[{Colors.ERROR}]💀 Cookie đã hết hạn!')
                    # Xóa file cookie cũ
                    cookie_file = f'COOKIEINS{self.account_id}.txt'
                    if os.path.exists(cookie_file):
                        os.remove(cookie_file)
                    return False
                else:
                    return False
                    
            except Exception as e:
                console.print(f"[{Colors.ERROR}]❌ Lỗi like: {str(e)}")
                return False
        
        return False

    def complete_job(self, ads_id: str) -> tuple[bool, int]:
        """Hoàn thành job và nhận thưởng"""
        url = 'https://gateway.golike.net/api/advertising/publishers/instagram/complete-jobs'
        json_data = {
            'instagram_account_id': self.account_id,
            'instagram_users_advertising_id': ads_id,
            'async': True,
            'data': 'null',
        }
        
        try:
            time.sleep(2)  # Chờ một chút trước khi complete
            response = self.session.post(url, headers=self.headers, json=json_data, timeout=15)
            result = response.json()
            
            if result.get('success'):
                prices = result.get('data', {}).get('prices', 0)
                return True, prices
            else:
                return False, 0
                
        except Exception as e:
            console.print(f"[{Colors.ERROR}]❌ Lỗi complete job: {str(e)}")
            return False, 0

    def skip_job(self, ads_id: str, account_id: str, object_id: str, job_type: str) -> bool:
        """Skip job nếu không thể hoàn thành"""
        try:
            skip_url = 'https://gateway.golike.net/api/advertising/publishers/instagram/skip-jobs'
            params = {
                'ads_id': ads_id,
                'account_id': account_id,
                'object_id': object_id,
                'async': 'true',
                'data': 'null',
                'type': job_type,
            }
            
            response = self.session.post(skip_url, params=params, timeout=10)
            result = response.json()
            
            if result.get('status') == 200:
                console.print(f"[{Colors.WARNING}]⚠️  Đã skip job: {result.get('message', '')}")
                return True
            return False
            
        except Exception as e:
            console.print(f"[{Colors.ERROR}]❌ Lỗi skip job: {str(e)}")
            return False

    def run_instagram_automation(self) -> None:
        """Chạy automation chính cho Instagram"""
        # Lấy danh sách tài khoản Instagram
        accounts = self.get_instagram_accounts()
        if not accounts:
            return
        
        # Chọn tài khoản
        account_index = self.display_instagram_accounts(accounts)
        if account_index is None:
            return
        
        selected_account = accounts[account_index]
        self.account_id = str(selected_account['id'])
        username = selected_account['instagram_username']
        
        console.clear()
        self.create_beautiful_banner()
        
        # Lấy cookie Instagram
        cookie = self.get_instagram_cookie(self.account_id)
        if not cookie:
            return
        
        # Tạo headers cho Instagram
        instagram_headers = self.create_instagram_headers(cookie)
        if not instagram_headers:
            return
        
        console.clear()
        self.create_beautiful_banner()
        
        # Lấy cấu hình
        num_jobs, delay = self.get_job_configuration()
        if num_jobs == 0:
            return
        
        console.clear()
        
        # Tạo bảng kết quả với design mới
        result_table = Table(
            title=f"[bold green]📊 KẾT QUẢ THỰC HIỆN - @{username}",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold blue",
            title_style="bold green"
        )
        
        result_table.add_column("[bold blue]#", style="cyan", no_wrap=True, width=5)
        result_table.add_column("[bold yellow]⏰ Time", style="yellow", width=12)
        result_table.add_column("[bold green]📋 Status", style="green", width=15)
        result_table.add_column("[bold red]🎯 Type", style="red", width=12)
        result_table.add_column("[bold cyan]💰 Reward", style="cyan", width=12)
        result_table.add_column("[bold magenta]💎 Total", style="magenta", width=15)
        result_table.add_column("[bold blue]📊 Progress", style="blue", width=20)
        
        total_earned = 0
        completed_jobs = 0
        failed_jobs = 0
        
        # Panel thông tin bắt đầu
        start_panel = Panel(
            f"[bold green]🚀 BẮT ĐẦU AUTOMATION\n\n"
            f"[yellow]📊 Target jobs: [bold cyan]{num_jobs}\n"
            f"[yellow]⏱️  Delay: [bold cyan]{delay}s\n"
            f"[yellow]👤 Account: [bold cyan]@{username}\n"
            f"[yellow]🆔 ID: [bold cyan]{self.account_id}",
            title="[bold blue]🤖 INSTAGRAM AUTOMATION",
            border_style="blue"
        )
        console.print(start_panel)
        console.print()
        
        # Chạy automation với Live table
        with Live(result_table, refresh_per_second=2, console=console) as live:
            for i in range(num_jobs):
                try:
                    # Lấy job mới
                    job_url = 'https://gateway.golike.net/api/advertising/publishers/instagram/jobs'
                    params = {
                        'instagram_account_id': self.account_id,
                        'data': 'null'
                    }
                    
                    response = self.session.get(job_url, headers=self.headers, params=params, timeout=15)
                    job_result = response.json()
                    
                    if job_result.get('status') != 200:
                        console.print(f"[{Colors.WARNING}]⚠️  Không có job mới, chờ 10s...")
                        time.sleep(10)
                        continue
                    
                    job_data = job_result.get('data', {})
                    if not job_data:
                        console.print(f"[{Colors.WARNING}]⚠️  Job data empty, skip...")
                        continue
                    
                    ads_id = job_data.get('id')
                    job_type = job_data.get('type')
                    object_id = job_data.get('object_id')
                    
                    # Thực hiện hành động Instagram
                    action_success = self.perform_instagram_action(job_data, instagram_headers)
                    
                    if action_success:
                        # Chờ delay
                        self.enhanced_countdown(delay, "Đang xử lý job")
                        
                        # Complete job
                        complete_success, reward = self.complete_job(ads_id)
                        
                        current_time = datetime.now().strftime("%H:%M:%S")
                        
                        if complete_success:
                            completed_jobs += 1
                            total_earned += reward
                            progress = f"{completed_jobs}/{num_jobs} ({(completed_jobs/num_jobs)*100:.1f}%)"
                            
                            # Icon cho type
                            type_icon = "👥 Follow" if job_type == 'follow' else "❤️  Like"
                            
                            result_table.add_row(
                                str(completed_jobs),
                                current_time,
                                "[green]✅ Success",
                                f"[red]{type_icon}",
                                f"[cyan]+{reward}",
                                f"[magenta]{total_earned:,}",
                                f"[blue]{progress}"
                            )
                        else:
                            failed_jobs += 1
                            # Skip job nếu complete không thành công
                            self.skip_job(ads_id, self.account_id, object_id, job_type)
                            
                            result_table.add_row(
                                str(completed_jobs + failed_jobs),
                                current_time,
                                "[red]❌ Failed",
                                f"[red]{job_type}",
                                "[red]0",
                                f"[magenta]{total_earned:,}",
                                f"[red]Failed: {failed_jobs}"
                            )
                    else:
                        failed_jobs += 1
                        # Skip job nếu action không thành công
                        self.skip_job(ads_id, self.account_id, object_id, job_type)
                    
                    live.update(result_table)
                    
                except KeyboardInterrupt:
                    console.print(f"\n[{Colors.WARNING}]⚠️  Đã dừng automation theo yêu cầu người dùng!")
                    break
                except Exception as e:
                    console.print(f"[{Colors.ERROR}]❌ Lỗi trong vòng lặp: {str(e)}")
                    time.sleep(5)
                    continue
        
        # Hiển thị kết quả cuối cùng
        self.display_final_results(completed_jobs, failed_jobs, total_earned, username)

    def display_final_results(self, completed: int, failed: int, total_earned: int, username: str) -> None:
        """Hiển thị kết quả cuối cùng"""
        success_rate = (completed / (completed + failed) * 100) if (completed + failed) > 0 else 0
        
        # Statistics table
        stats_table = Table(
            title="[bold green]📈 THỐNG KÊ CHI TIẾT",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold blue"
        )
        
        stats_table.add_column("[bold yellow]Thống kê", style="yellow", width=20)
        stats_table.add_column("[bold green]Kết quả", style="green", width=25)
        
        stats_table.add_row("👤 Tài khoản", f"[bold cyan]@{username}")
        stats_table.add_row("✅ Job thành công", f"[bold green]{completed}")
        stats_table.add_row("❌ Job thất bại", f"[bold red]{failed}")
        stats_table.add_row("📊 Tỷ lệ thành công", f"[bold yellow]{success_rate:.1f}%")
        stats_table.add_row("💰 Tổng tiền kiếm", f"[bold green]{total_earned:,} VNĐ")
        stats_table.add_row("⏰ Thời gian kết thúc", f"[bold cyan]{datetime.now().strftime('%H:%M:%S')}")
        
        finish_panel = Panel(
            f"[bold green]🎉 HOÀN THÀNH AUTOMATION!\n\n"
            f"[yellow]Cảm ơn bạn đã sử dụng tool! 💝\n"
            f"[cyan]Hãy ủng hộ tác giả bằng cách follow:\n"
            f"[blue]📱 Telegram: @doanhvip1\n"
            f"[red]🎵 TikTok: @doanh21105",
            title="[bold blue]📋 THANK YOU",
            border_style="green"
        )
        
        console.print(stats_table)
        console.print()
        console.print(finish_panel)
def main():
    """Hàm main chính của chương trình"""
    bot = InstagramBot()
    
    try:
        bot.create_beautiful_banner()
        
        # Kiểm tra file auth
        auth_file = 'user.txt'
        if not os.path.exists(auth_file):
            # Đăng nhập lần đầu
            console.print(Panel(
                "[bold yellow]🔑 ĐĂNG NHẬP GOLIKE\n\n"
                "[white]Hướng dẫn lấy Authorization:\n"
                "[cyan]1. Vào https://app.golike.net\n"
                "[cyan]2. Nhấn F12 → Network → Reload trang\n"
                "[cyan]3. Tìm request có Authorization trong Headers\n"
                "[cyan]4. Copy giá trị Authorization và paste vào đây",
                title="[bold green]🚪 XÁC THỰC",
                border_style="green"
            ))
            
            auth_token = Prompt.ask("[bold green]🔑 Nhập Authorization Token", password=True)
            
            # Validate token
            if not bot.validate_auth_token(auth_token):
                console.print(Panel(
                    "[bold red]❌ TOKEN KHÔNG HỢP LỆ!\n\n"
                    "[yellow]Vui lòng kiểm tra lại Authorization token.",
                    title="[bold red]🚫 LỖI XÁC THỰC",
                    border_style="red"
                ))
                return
            
            # Lưu token
            with open(auth_file, 'w', encoding='utf-8') as f:
                f.write(auth_token)
        
        # Đọc token từ file
        with open(auth_file, 'r', encoding='utf-8') as f:
            auth_token = f.read().strip()
        
        # Thiết lập session và headers
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        bot.headers = {
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
            'Referer': 'https://app.golike.net/',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': random.choice(user_agents),
            'Authorization': auth_token,
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        # Xác thực token
        with Status("[bold blue]🔍 Đang xác thực token...", console=console, spinner="dots"):
            response = bot.session.get(
                'https://gateway.golike.net/api/users/me',
                headers=bot.headers,
                timeout=15
            )
        
        if response.status_code != 200:
            console.print(Panel(
                "[bold red]❌ LỖI NETWORK!\n\n"
                f"[yellow]Status code: {response.status_code}",
                title="[bold red]🌐 LỖI KẾT NỐI",
                border_style="red"
            ))
            return
            
        user_data = response.json()
        
        if user_data.get('status') == 200:
            # Đăng nhập thành công
            with Progress(
                SpinnerColumn("dots"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=30),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("[green]Đang đăng nhập...", total=100)
                for i in range(100):
                    time.sleep(0.02)
                    progress.update(task, advance=1)
            
            console.print(f"[{Colors.SUCCESS}]✅ ĐĂNG NHẬP THÀNH CÔNG!")
            time.sleep(1)
            
            console.clear()
            bot.create_beautiful_banner()
            
            # Lưu thông tin user
            bot.user_info = user_data.get('data', {})
            username = bot.user_info.get('username', 'Unknown')
            coin = bot.user_info.get('coin', 0)
            user_id = bot.user_info.get('id', 'Unknown')
            
            # Hiển thị thông tin tài khoản
            account_table = Table(
                title="[bold cyan]👤 THÔNG TIN TÀI KHOẢN GOLIKE",
                box=box.DOUBLE_EDGE,
                show_header=True,
                header_style="bold blue"
            )
            
            account_table.add_column("[bold yellow]🔹 Thuộc tính", style="yellow", width=20)
            account_table.add_column("[bold green]🔸 Giá trị", style="green", width=30)
            
            account_table.add_row("👤 Username", f"[bold cyan]{username}")
            account_table.add_row("💰 Số dư hiện tại", f"[bold yellow]{coin:,} VNĐ")
            account_table.add_row("🆔 User ID", f"[bold magenta]{user_id}")
            account_table.add_row("⏰ Thời gian đăng nhập", f"[bold cyan]{datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
            
            console.print(account_table)
            console.print()
            
            # Menu chính với design đẹp hơn
            menu_options = [
                "[green]1.[/] [bold white]🎯 Chạy Tool Instagram Automation",
                "[red]2.[/] [bold white]🗑️  Xóa Token và đăng nhập lại",
                "[yellow]3.[/] [bold white]ℹ️  Xem thông tin tài khoản",
                "[blue]4.[/] [bold white]🚪 Thoát chương trình"
            ]
            
            menu_panel = Panel(
                "\n".join(menu_options),
                title="[bold blue]📋 MENU CHÍNH",
                border_style="blue",
                padding=(1, 2)
            )
            console.print(menu_panel)
            
            try:
                choice = IntPrompt.ask(
                    "[bold white]🎮 Chọn chức năng",
                    choices=["1", "2", "3", "4"],
                    default="1"
                )
                
                if choice == 1:
                    console.clear()
                    bot.run_instagram_automation()
                    
                elif choice == 2:
                    if Confirm.ask("[bold yellow]⚠️  Bạn có chắc muốn xóa token?"):
                        os.remove(auth_file)
                        console.print(f"[{Colors.SUCCESS}]✅ Đã xóa token! Khởi động lại để đăng nhập mới.")
                    
                elif choice == 3:
                    console.clear()
                    console.print(account_table)
                    Prompt.ask("\n[bold blue]Nhấn Enter để tiếp tục...")
                    
                elif choice == 4:
                    console.print(f"[{Colors.INFO}]👋 Cảm ơn bạn đã sử dụng tool!")
                    return
                    
            except KeyboardInterrupt:
                console.print(f"\n[{Colors.WARNING}]⚠️  Đã hủy thao tác!")
                
        else:
            console.print(Panel(
                "[bold red]❌ ĐĂNG NHẬP THẤT BẠI!\n\n"
                "[yellow]Token không hợp lệ hoặc đã hết hạn.",
                title="[bold red]🚫 LỖI XÁC THỰC",
                border_style="red"
            ))
            
            if os.path.exists(auth_file):
                os.remove(auth_file)
                console.print(f"[{Colors.INFO}]🗑️  Đã xóa token cũ. Khởi động lại để đăng nhập mới.")
                
    except KeyboardInterrupt:
        console.print(f"\n[{Colors.WARNING}]👋 Đã thoát chương trình!")
    except Exception as e:
        console.print(f"[{Colors.ERROR}]❌ Lỗi không mong muốn: {str(e)}")
        console.print(f"[{Colors.INFO}]💡 Vui lòng báo lỗi cho tác giả!")

if __name__ == "__main__":
    main()