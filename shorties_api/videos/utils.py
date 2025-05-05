import os
import subprocess
import tempfile
from django.conf import settings
import logging
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

logger = logging.getLogger(__name__)

def generate_thumbnail(video_file, video_id, timestamp=1.0):
    """
    Generate a thumbnail for a video using ffmpeg
    
    Args:
        video_file: Path to the video file
        video_id: Video ID for file naming
        timestamp: Time position in seconds for the thumbnail
        
    Returns:
        BytesIO object containing the thumbnail image
    """
    from videos.models import Video
    
    try:
        video_instance = Video.objects.get(id=video_id)
        
        # Create a temporary file for the thumbnail
        with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_thumb:
            # Generate thumbnail using ffmpeg
            subprocess.check_call([
                'ffmpeg', '-y',
                '-i', video_file.path,
                '-ss', str(timestamp),
                '-vframes', '1',
                '-vf', 'scale=720:-1',
                temp_thumb.name
            ])
            
            # Open and compress the thumbnail
            with Image.open(temp_thumb.name) as img:
                # Resize if needed
                if img.height > 1280:
                    img = img.resize(
                        (int(img.width * 1280 / img.height), 1280),
                        Image.LANCZOS
                    )
                
                # Save to BytesIO
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG', quality=85)
                thumb_io.seek(0)
                
                # Generate filename
                thumb_filename = f"{uuid.uuid4()}.jpg"
                
                # Save to the Video model
                video_instance.thumbnail.save(
                    thumb_filename,
                    ContentFile(thumb_io.read()),
                    save=True
                )
                
                return True
                
    except Exception as e:
        logger.error(f"Error generating thumbnail for video {video_id}: {str(e)}")
        return False


def get_video_info(video_path):
    """
    Get video information using ffprobe
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary containing video info (duration, width, height)
    """
    try:
        # Get video duration
        duration_output = subprocess.check_output([
            'ffprobe', '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            video_path
        ]).decode('utf-8').strip()
        
        # Get video dimensions
        dimensions_output = subprocess.check_output([
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0:s=x',
            video_path
        ]).decode('utf-8').strip()
        
        # Parse dimensions
        width, height = dimensions_output.split('x')
        
        return {
            'duration': float(duration_output),
            'width': int(width),
            'height': int(height)
        }
        
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return {
            'duration': 0,
            'width': 0,
            'height': 0
        }


def transcode_video(video_file, quality, video_id):
    """
    Transcode video to different quality levels
    
    Args:
        video_file: Path to the video file
        quality: Quality level ('low', 'medium', 'high')
        video_id: Video ID for file naming
        
    Returns:
        Path to the transcoded video file
    """
    from videos.models import Video
    
    try:
        video_instance = Video.objects.get(id=video_id)
        quality_settings = settings.VIDEO_QUALITIES.get(quality)
        
        if not quality_settings:
            raise ValueError(f"Invalid quality level: {quality}")
        
        # Create temp file for transcoded video
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
            temp_video_path = temp_video.name
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-i', video_file.path,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-b:v', quality_settings['bitrate'],
                '-maxrate', quality_settings['bitrate'],
                '-bufsize', f"{int(float(quality_settings['bitrate'][:-1]) * 1.5)}k",
                '-vf', f"scale=-1:{quality_settings['height']}",
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                temp_video_path
            ]
            
            # Run ffmpeg
            subprocess.check_call(cmd)
            
            # Get field name based on quality
            field_name = f"video_{quality}"
            
            # Save to the Video model
            with open(temp_video_path, 'rb') as f:
                file_content = ContentFile(f.read())
                getattr(video_instance, field_name).save(
                    f"{uuid.uuid4()}.mp4",
                    file_content,
                    save=True
                )
            
            # Clean up temp file
            os.unlink(temp_video_path)
            
            return True
            
    except Exception as e:
        logger.error(f"Error transcoding video {video_id} to {quality}: {str(e)}")
        return False


def process_video(video_id):
    """
    Process a video after upload.
    
    Args:
        video_id: ID of the video to process
        
    Processing includes:
    1. Extracting video metadata (duration, dimensions)
    2. Generating a thumbnail
    3. Transcoding to different quality levels
    """
    from videos.models import Video
    
    try:
        video = Video.objects.get(id=video_id)
        
        # Update processing status
        video.processing_status = 'processing'
        video.save(update_fields=['processing_status'])
        
        # Extract video metadata
        video_info = get_video_info(video.video_file.path)
        video.duration = video_info['duration']
        video.width = video_info['width']
        video.height = video_info['height']
        video.save(update_fields=['duration', 'width', 'height'])
        
        # Generate thumbnail (at 1 second mark)
        generate_thumbnail(video.video_file, video_id, timestamp=1.0)
        
        # Transcode to different qualities
        for quality in ['low', 'medium', 'high']:
            transcode_video(video.video_file, quality, video_id)
        
        # Update processing status to ready
        video.processing_status = 'ready'
        video.save(update_fields=['processing_status'])
        
        # Update user's video count
        user = video.user
        user.video_count = Video.objects.filter(user=user).count()
        user.save(update_fields=['video_count'])
        
        logger.info(f"Successfully processed video {video_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        
        # Update processing status to failed
        try:
            video = Video.objects.get(id=video_id)
            video.processing_status = 'failed'
            video.save(update_fields=['processing_status'])
        except:
            pass
            
        return False
