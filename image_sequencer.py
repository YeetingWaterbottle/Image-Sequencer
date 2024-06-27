import ffmpeg
import pathlib


class ImageSequencer:
    """
    A class to generate videos using ffmpeg from a sequence of image files.
    """

    def __init__(self, concat_filename: str = "concat.txt"):
        """
        Initialize the VideoGenerator with a default concat filename.

        Args:
            concat_filename (str, optional): Filename for the ffmpeg concat file. Defaults to "concat.txt".
        """
        self.concat_filename = concat_filename
        self.files = []  # List of file paths to be concatenated
        self.duration = None  # Duration shown for each file (1/fps)
        self.output_filename = "output.mp4"  # Output video filename
        self.output_framerate = 25.0  # Output framerate for the video
        self.output_resolution = (None, None)  # Output resolution for the video
        self.force_overwrite = False  # Force overwrite existing file with video

    def set_concat_filename(self, concat_filename: str) -> None:
        """
        Set the filename for the ffmpeg concat file.

        Args:
            concat_filename (str): Filename for the ffmpeg concat file.
        """
        self.concat_filename = concat_filename

    def set_files(self, files: list[str]) -> None:
        """
        Set the list of file paths and duration for each file.

        Args:
            files (list[str]): List of file paths to be concatenated.
        """
        self.files = files

    def set_input_framerate(self, input_framerate: float) -> None:
        """
        Set the output framerate for the generated video.

        Args:
            input_framerate (float): Input framerate of the images.
        """
        self.duration = 1 / input_framerate

    def set_output_filename(self, output_filename: str) -> None:
        """
        Set the output filename for the generated video.

        Args:
            output_filename (str): Output video filename.
        """
        self.output_filename = output_filename

    def set_output_framerate(self, output_framerate: float) -> None:
        """
        Set the output framerate for the generated video.

        Args:
            output_framerate (float): Output framerate for the video.
        """
        self.output_framerate = output_framerate

    def set_output_resolution(self, x_res: int, y_res: int) -> None:
        """
        Set the output resolution for the generated video.

        Args:
            x_res (int): Horizontal resolution for the video.
            y_res (int): Vertical resolution for the video.
        """
        self.output_resolution = (x_res, y_res)

    def set_force_overwrite(self, overwrite: bool) -> None:
        """
        Set the overwrite setting for ffmpeg.

        Args:
            overwrite (bool): Whether or not to overwrite any existing file with same name as output.
        """
        self.force_overwrite = overwrite

    def generate_concat(self) -> None:
        """
        Generate the ffmpeg concat file based on the current list of files and duration.
        """
        with open(self.concat_filename, "wt") as concat_file:
            for filename in self.files:
                concat_file.write(f"file '{pathlib.Path(filename).resolve()}'\n")
                concat_file.write(f"duration {self.duration}\n")

    def generate_video(self) -> None:
        """
        Generate a video using ffmpeg from the current concat file.
        """
        self.generate_concat()

        res_x, res_y = self.output_resolution
        res_filter = (
            f"scale={res_x}:{res_y}" if None not in self.output_resolution else "null"
        )

        (
            ffmpeg.input(self.concat_filename, format="concat", safe=0)
            .output(
                self.output_filename,
                c="libx264",
                pix_fmt="yuv420p",
                r=self.output_framerate,
                vf=f"{res_filter}, crop=trunc(iw/2)*2:trunc(ih/2)*2, setsar=1",  # crops the input so odd numbered resolution would work
            )
            .run(overwrite_output=self.force_overwrite)
        )

    def generate_ffmpeg_command(self) -> list[str]:
        """
        Generate the ffmpeg command as a list to convert the images to video.

        Returns:
            list[str]: The ffmpeg command as a list of strings.
        """
        ffmpeg_command = [
            "ffmpeg",
            "-f",
            "concat",
            "-i",
            str(pathlib.Path(self.concat_filename).resolve()),  # gets the absolute path
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",  # sets output framerate
            str(self.output_framerate),
        ]

        if None not in self.output_resolution:
            res_x, res_y = self.output_resolution

            res_filter = f"scale={res_x}:{res_y}"
            ffmpeg_command.extend(
                [
                    "-vf",  # sets output resolution
                    f"{res_filter}, crop=trunc(iw/2)*2:trunc(ih/2)*2, setsar=1",  # crops the input so odd numbered resolution would work
                ]
            )

        if self.force_overwrite:
            # Force overwrite video file
            ffmpeg_command.append("-y")

        ffmpeg_command.append(self.output_filename)

        return ffmpeg_command
