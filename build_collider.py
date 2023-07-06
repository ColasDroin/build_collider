#### Imports
import yaml
import sys
import importlib
import os
import xtrack as xt

""" This class builds and configure a collider from a 'base collider' json file, along with a 
configuration file."""


#### Build collider class
class BuildCollider:
    def __init__(self, path_configuration):
        """Initialize the BuildCollider class."""

        # Configuration path
        self.path_configuration = path_configuration

        # Load configuration
        self.configuration = self.load_configuration()

        # Correct path in configuration
        self.correct_configuration()

        # Load and tune collider
        self.collider = self.load_and_tune_collider()

        # Compute collider without beam-beam
        self.collider_without_bb = xt.Multiline.from_dict(self.collider.to_dict())
        self.collider_without_bb.build_trackers()
        self.collider_without_bb.vars["beambeam_scale"] = 0

    def load_configuration(self):
        """Loads the configuration from a yaml file."""
        with open(self.path_configuration, "r") as fid:
            configuration = yaml.safe_load(fid)
        return configuration

    def correct_configuration(self):
        """Corrects the paths in the configuration file (from relative to absolute)."""
        self.configuration["config_simulation"]["collider_file"] = (
            self.path_configuration.split("config.yaml")[0]
            + self.configuration["config_simulation"]["collider_file"]
        )

    def load_and_tune_collider(self):
        """Build the collider using the same script as in the initial configuration file."""

        # Path of the 2_configure_and_track file
        path_configure_and_track = self.path_configuration.split("config.yaml")[0]
        name_module = "2_configure_and_track.py"
        # Check that the twiss and track file exists
        if not os.path.exists(path_configure_and_track + name_module):
            raise ValueError(
                "The 2_configure_and_track file does not exist in the same directory as the config"
                " file. No collider can be built ensuring reproducibility."
            )
        else:
            # Add to sys
            sys.path.insert(1, path_configure_and_track)

            # Import the module
            configure_and_track = importlib.import_module("2_configure_and_track")

        # Build collider
        collider, _ = configure_and_track.configure_collider(
            self.configuration["config_simulation"],
            self.configuration["config_collider"],
            save_collider=False,
            return_collider_before_bb=False,
        )

        # Remove the folder "correction" which was created during the process
        os.system("rm -rf correction")
        # Remove other temporary files
        os.system("rm -rf .__*")

        return collider

    def dump_collider(self, prefix=None, suffix="collider.json"):
        """Dumps the collider to a json file."""
        path_collider = (
            self.path_configuration.split("/scans/")[1].split("config.yaml")[0].replace("/", "_")
        )
        if prefix is not None:
            path_collider = prefix + path_collider + suffix
        self.collider.to_json(path_collider)

        return path_collider


if __name__ == "__main__":
    # Load collider
    path_config = "/afs/cern.ch/work/c/cdroin/private/example_DA_study/master_study/scans/opt_flathv_75_1500_withBB_chroma5_1p4_eol_tune_intensity/base_collider/xtrack_0000/config.yaml"
    build_collider = BuildCollider(path_config)

    # Dump collider
    # path_collider = build_collider.dump_collider()
