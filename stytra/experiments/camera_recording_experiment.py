from multiprocessing import Event, Queue
from stytra.collectors import FramerateQueueAccumulator

from stytra.hardware.video.write import video_writers_dict

from stytra.experiments.tracking_experiments import CameraVisualExperiment
from stytra.tracking.tracking_process import DispatchProcess


class VideoRecordingExperiment(CameraVisualExperiment):
    def __init__(self, *args, **kwargs):
        """
        :param video_file: if not using a camera, the video file
        file for the test input
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.finished_evt = Event()
        self.saving_evt = Event()

        self.frame_dispatcher = DispatchProcess(
            self.camera.frame_queue, self.finished_evt, self.saving_evt
        )

        # start frame dispatcher process:
        self.frame_dispatcher.start()

        # Create and connect framerate accumulator:
        self.acc_tracking_framerate = FramerateQueueAccumulator(
            self,
            queue=self.frame_dispatcher.framerate_queue,
            name="tracking",
            goal_framerate=kwargs["camera"].get("min_framerate", None),
        )
        self.gui_timer.timeout.connect(self.acc_tracking_framerate.update_list)

        self.set_id()
        video_writer_class = video_writers_dict[kwargs["recording"].pop(
            "extension")]
        self.video_writer = video_writer_class(
            self.frame_dispatcher.output_frame_queue,
            self.finished_evt, self.saving_evt, **kwargs["recording"]
        )

        self.video_writer.start()

    def start_protocol(self):
        self.saving_evt.set()
        self.video_writer.reset_signal.set()
        self.video_writer.filename_queue.put(self.folder_name)
        super().start_protocol()

    def end_protocol(self, save=True):
        self.saving_evt.clear()

        super().end_protocol()

    def wrap_up(self, *args, **kwargs):
        self.video_writer.finished_signal.set()
        self.video_writer.join()
        print("closed")
        super().wrap_up(*args, **kwargs)
