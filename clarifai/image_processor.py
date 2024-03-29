import asyncio
from io import BytesIO
from math import floor
from typing import List

import cv2
import imageio.v3 as iio
import numpy as np
from PIL import Image

from logger import CustomLogger

video_processor_logger = CustomLogger("VideoProcessor").get_logger()


class AsyncVideoProcessor:
    """this class is for handling videos to select the best frame for processing"""

    # @profile  # noqa: F821 # type: ignore
    async def process_video(self, video_bytes: bytes) -> np.ndarray:
        video_processor_logger.info("Began processing video")
        try:
            frames = await asyncio.to_thread(self._bytes_to_frames, video_bytes)
            gray_frames = await asyncio.to_thread(self._grays_scale_image, frames)
            best_frame_index = await asyncio.to_thread(
                self._get_sharpest_frame, gray_frames
            )
            best_frame = frames[best_frame_index]
            # return cv2.resize(best_frame, (0, 0), fx=0.95, fy=0.95)
            video_processor_logger.info("Finished processing video successfully")
            return best_frame
        except Exception as e:
            video_processor_logger.error("VideoProcessorError", exc_info=True)
            raise e

    def _bytes_to_frames(self, video_bytes: bytes) -> List[np.ndarray]:
        frames = iio.imread(video_bytes, index=None, format_hint=".mp4")
        return frames  # type: ignore

    def _grays_scale_image(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        return [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in frames]

    def _get_sharpest_frame(self, gray_frames: List[np.ndarray]):
        sharpest_frame_index = np.argmax(
            [cv2.Laplacian(gray_frame, cv2.CV_64F).var() for gray_frame in gray_frames]
        )
        # print(sharpest_frame_index)
        return sharpest_frame_index

    # @profile  # noqa: F821 # type: ignore
    def convert_result_image_to_bytes(self, image: np.ndarray) -> bytes:
        image_pil: Image.Image = Image.fromarray(image)
        # initial_size = len(image_pil.tobytes()) / 1024
        x, y = image_pil.size
        if image_pil.width > image_pil.height:
            x2, y2 = floor(x - 50), floor(y - 20)
        else:
            x2, y2 = floor(x - 20), floor(y - 50)
        image_pil.resize((x2, y2), Image.LANCZOS)
        buffer = BytesIO()
        image_pil.save(buffer, format="PNG", optimize=True, quality=75)
        image_bytes = buffer.getvalue()
        # Path("image.png").write_bytes(image_bytes)
        # final_size = len(image_bytes) / 1024
        # print(f"Image size reduced from {initial_size}KB to {final_size}KB")
        return image_bytes
