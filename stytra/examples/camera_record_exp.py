from multiprocessing import Event
from stytra.collectors import FramerateQueueAccumulator

import qdarkstyle
from PyQt5.QtWidgets import QApplication
from stytra.hardware.video.write import VideoWriter
from stytra.stimulation import Protocol, Pause
from stytra.stimulation.stimuli import FullFieldVisualStimulus
from lightparam import Param
from pathlib import Path
from stytra.experiments.tracking_experiments import CameraVisualExperiment
from stytra.tracking.tracking_process import DispatchProcess
from stytra import Stytra

# Here ve define an empty protocol:
class PauseProtocol(Protocol):
    name = "camera_recording_protocol"  # every protocol must have a name.
    stytra_config = dict(camera=dict(
            video_file=str(Path(__file__).parent / "assets" / "fish_free_compressed.h5"),
            min_framerate=100),
        recording=dict(extension="mp4"))
    def __init__(self):
        super().__init__()
        self.period_sec = Param(10., limits=(0.2, None))

    def get_stim_sequence(self):
        return [Pause(duration=self.period_sec), ]

if __name__ == "__main__":
    st = Stytra(protocol=PauseProtocol())