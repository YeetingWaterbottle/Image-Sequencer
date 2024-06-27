import dearpygui.dearpygui as dpg
import os
import pathlib
import xdialog

import image_sequencer

image_sequencer = image_sequencer.ImageSequencer()


def select_files(selection_type: str) -> None:
    """
    Opens a file dialogue to select target files and folders

    Args:
        selection_type (str): Type of selection (individual, folders, clear).

    Raises:
        ValueError: If "selection_type" variable does not match the possible actions
    """

    append_files: bool = dpg.get_value("file_append_checkbox")

    file_paths = []

    if selection_type == "individual":
        file_paths = xdialog.open_file(
            "Select Images",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")],
            multiple=True,
        )

    elif selection_type == "folder":
        folder_path = xdialog.directory("Select Image Folder")
        if os.path.isdir(folder_path):
            file_paths = [
                joined_path
                for f in os.listdir(folder_path)
                if os.path.isfile(joined_path := os.path.join(folder_path, f))
            ]

    elif selection_type == "clear":
        file_paths = []
        append_files = False

    else:
        raise ValueError("Invalid selection_type parameter provided")

    formatted_paths = [str(pathlib.Path(file).resolve()) for file in file_paths]

    if append_files:
        existing_files = dpg.get_item_configuration("file_list")["items"]
        formatted_paths = existing_files + formatted_paths

    dpg.configure_item("file_list", items=formatted_paths)

    update_file_label()

    image_sequencer.set_files(formatted_paths)


def sort_input_files() -> None:
    """
    Sorts the input files based on the filename
    """
    files: list[str] = dpg.get_item_configuration("file_list")["items"]

    dpg.configure_item("file_list", items=sorted(files))


def remove_selected_file() -> None:
    """
    Removes the selected item in file list
    """
    files: list[str] = dpg.get_item_configuration("file_list")["items"]
    selected_file: str = dpg.get_value("file_list")

    try:
        file_index = files.index(selected_file)
        files.pop(file_index)  # Removes selected file
        dpg.configure_item("file_list", items=files)  # Sets updated list

        if file_index >= len(files):  # If removed item is last in list
            file_index -= 1  # Decrement index so last item would be selected

        dpg.set_value(
            "file_list", files[file_index]
        )  # Sets the selected item to be below the removed item
    except ValueError:
        print("Selected file not found")
    except IndexError:
        print("Selected index not found")
    except Exception as e:
        print(f"Unknown error occured: {e}")


def update_file_label() -> None:
    """
    Update the listbox label with the number of items
    """
    file_count = len(dpg.get_item_configuration("file_list")["items"])

    if file_count == 0:
        message = "No File Selected"
    else:
        message = f"{file_count} File{'s' if file_count > 1 else ''} Selected"

    dpg.set_value("file_count_label", message)

    update_video_length_label()


def update_video_length_label() -> None:
    """
    Updates the video length info
    """
    file_count = len(dpg.get_item_configuration("file_list")["items"])
    input_fps: int = dpg.get_value("source_fps_slider")

    video_length = (1 / input_fps) * file_count

    message = f"Video Length: {round(video_length, 2)}(s)"

    dpg.set_value("video_length_label", message)


def set_output_parameter() -> None:
    """
    Assigns GUI values to ImageSequencer object for output
    """
    input_fps: int = dpg.get_value("source_fps_slider")
    image_sequencer.set_input_framerate(input_fps)

    output_fps: int = dpg.get_value("target_fps_slider")
    image_sequencer.set_output_framerate(output_fps)

    output_filename: str = dpg.get_value("output_name_input")
    image_sequencer.set_output_filename(output_filename)

    use_custom_res: bool = dpg.get_value("custom_resolution_checkbox")

    if use_custom_res:
        x_res = dpg.get_value("horizontal_resolution_input")
        y_res = dpg.get_value("vertical_resolution_input")

        if dpg.get_value("scale_x_res_checkbox"):
            x_res = -1

        if dpg.get_value("scale_y_res_checkbox"):
            y_res = -1

        image_sequencer.set_output_resolution(x_res, y_res)
    else:
        image_sequencer.set_output_resolution(None, None)


def generate_action(generate_target: str) -> None:
    """
    Executes video generation based on parameter

    Args:
        generate_target (str): Determines what to execute (concat, video, command)

    Raises:
        ValueError: If "generate_target" variable does not match the possible actions
    """
    set_output_parameter()

    if generate_target == "concat":
        image_sequencer.generate_concat()
    elif generate_target == "video":
        image_sequencer.generate_video()
    elif generate_target == "command":
        print(" ".join(image_sequencer.generate_ffmpeg_command()))
    else:
        raise ValueError("Invalid generate_target parameter provided")


dpg.create_context()

# Adding custom fonts
with dpg.font_registry():
    default_font = dpg.add_font("assets/Ubuntu-Regular.ttf", 16)


# Start of GUI
with dpg.window(tag="root"):
    # File list buttons
    with dpg.collapsing_header(label="Import Files", default_open=True):
        with dpg.group(horizontal=True, tag="input_buttons"):
            dpg.add_button(
                label="Select File(s)",
                callback=lambda: select_files("individual"),
            )
            dpg.add_button(
                label="Load Folder",
                callback=lambda: select_files("folder"),
            )
            dpg.add_button(
                label="Clear Selected",
                callback=lambda: select_files("clear"),
            )
            dpg.add_checkbox(
                label="Append File",
                tag="file_append_checkbox",
            )

    # File list display
    with dpg.collapsing_header(label="File List", default_open=True):
        with dpg.group(horizontal=True):
            dpg.add_listbox(num_items=12, tag="file_list")

            # Info display
            with dpg.group():
                dpg.add_text("No File Selected", tag="file_count_label")
                dpg.add_text("Video Length: 0.0(s)", tag="video_length_label")
                dpg.add_button(label="Sort Files", callback=sort_input_files)
                dpg.add_button(
                    label="Remove Selected File", callback=remove_selected_file
                )

    # Output parameters
    with dpg.collapsing_header(label="Output Parameters", default_open=True):
        with dpg.group(tag="output_parameter_input"):
            dpg.add_slider_int(
                label="Source FPS",
                default_value=25,
                min_value=1,
                max_value=60,
                tag="source_fps_slider",
                callback=update_video_length_label,
            )

            dpg.add_slider_int(
                label="Target FPS",
                default_value=25,
                min_value=1,
                max_value=60,
                tag="target_fps_slider",
            )

            dpg.add_input_text(
                label="Output Filename",
                default_value="output.mp4",
                tag="output_name_input",
            )

            # Set video output resolution
            with dpg.collapsing_header(label="Custom Resolution"):
                dpg.add_checkbox(
                    label="Use Custom Resolution",
                    tag="custom_resolution_checkbox",
                    callback=lambda _, use_custom_res: dpg.configure_item(
                        "custom_resolution_input_group", show=use_custom_res
                    ),
                )

                with dpg.group(tag="custom_resolution_input_group", show=False):
                    # Horizontal resolution settings
                    with dpg.group(horizontal=True):
                        dpg.add_input_int(
                            label="Horizontal Resolution",
                            default_value=1,
                            min_value=1,
                            min_clamped=True,
                            tag="horizontal_resolution_input",
                        )
                        dpg.add_checkbox(
                            label="Auto Scale Horizontal Resolution",
                            tag="scale_x_res_checkbox",
                            callback=lambda _, scale_x_res: dpg.configure_item(
                                "horizontal_resolution_input", show=not scale_x_res
                            ),
                        )

                    # Vertical resolution settings
                    with dpg.group(horizontal=True):
                        dpg.add_input_int(
                            label="Vertical Resolution",
                            default_value=1,
                            min_value=1,
                            min_clamped=True,
                            tag="vertical_resolution_input",
                        )
                        dpg.add_checkbox(
                            label="Auto Scale Vertical Resolution",
                            tag="scale_y_res_checkbox",
                            callback=lambda _, scale_y_res: dpg.configure_item(
                                "vertical_resolution_input", show=not scale_y_res
                            ),
                        )

    # Output buttons
    with dpg.collapsing_header(label="Output Actions", default_open=True):
        with dpg.group(horizontal=True):
            # Generate video
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Generate Video", callback=lambda: generate_action("video")
                )
                dpg.add_checkbox(
                    label="Overwrite if exist?",
                    callback=lambda _, overwrite: image_sequencer.set_force_overwrite(
                        overwrite
                    ),
                )

            # Advanced options
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Generate ffmpeg Command",
                    callback=lambda: generate_action("command"),
                )
                dpg.add_button(
                    label="Generate Concat. File",
                    callback=lambda: generate_action("concat"),
                )

    # Set fonts
    dpg.bind_font(default_font)


# Application themes
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)

        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 16)

        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)

        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 6)

        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 16, 8)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 4)


# Code for DearPyGUI
dpg.bind_theme(global_theme)

dpg.create_viewport(title="Image Sequencer")

dpg.setup_dearpygui()

dpg.show_viewport()

dpg.set_primary_window("root", True)
dpg.start_dearpygui()
dpg.destroy_context()
