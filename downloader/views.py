import os
import yt_dlp
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.conf import settings
from .models import VideoDownload

def home(request):
    # Yeh user ko main search page par le kar jayega
    return render(request, 'downloader/home.html')

def fetch_video_info(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        if not video_url:
            return redirect('home')
        
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Video ki details nikaalo bina download kiye
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'Awesome Video')
                formats = info.get('formats', [])
                
                available_formats = []
                
                # 🎵 JADOO 1: MP3 Audio ka VIP option sab se oopar daal diya!
                available_formats.append({
                    'format_id': 'bestaudio',
                    'resolution': '🎵 MP3 Audio Only',
                    'ext': 'mp3',
                    'filesize': 'N/A'
                })

                # 🎬 JADOO 2: Sirf MP4 Videos ko filter kiya
                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                        size_mb = round(f.get('filesize', 0) / (1024 * 1024), 2) if f.get('filesize') else 'N/A'
                        available_formats.append({
                            'format_id': f.get('format_id'),
                            'resolution': f"🎬 Video {f.get('resolution') or f.get('format_note')}",
                            'ext': 'mp4',
                            'filesize': size_mb
                        })
                
                context = {
                    'url': video_url,
                    'title': video_title,
                    'formats': available_formats
                }
                # HTML front-end par bhej do jahan user quality select karega
                return render(request, 'downloader/select_quality.html', context)
                
            except Exception as e:
                return HttpResponse(f"Oye Ustad, Link fetch karne mein error aaya: {e}")
                
    return redirect('home')

def download_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('url')
        format_id = request.POST.get('format_id')
        video_title = request.POST.get('title', 'video')
        
        # Laptop ki storage mein temporary folder banao
        download_dir = os.path.join(settings.BASE_DIR, 'downloads')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        }

        # 🎵 THEKEDARI HACK: Agar user ne MP3 select kiya hai
        if format_id == 'bestaudio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        # 🎬 THEKEDARI HACK: Agar Video select ki hai (Video + Audio FFMPEG merge karega)
        else:
            ydl_opts['format'] = f"{format_id}+bestaudio/best"
            ydl_opts['merge_output_format'] = 'mp4'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=True)
                
                # File ka exact naam uthao download hone ke baad
                if 'requested_downloads' in info:
                    filename = info['requested_downloads'][0]['filepath']
                else:
                    filename = ydl.prepare_filename(info)
                    if format_id == 'bestaudio':
                        filename = os.path.splitext(filename)[0] + '.mp3'
                    else:
                        filename = os.path.splitext(filename)[0] + '.mp4'
                
                # History database mein save karo
                VideoDownload.objects.create(
                    url=video_url,
                    title=video_title,
                    quality=format_id
                )
                
                # File open karke direct user ko download ke liye serve karo
                response = FileResponse(open(filename, 'rb'), as_attachment=True)
                return response
                
            except Exception as e:
                return HttpResponse(f"Download lagane mein koi masla hua: {e}")
                
    return redirect('home')