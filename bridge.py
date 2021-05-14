import argparse
import collections
import logging
import sys
import threading
from lume_model.utils import load_variables
import epics
import pandas

logger = logging.getLogger(__name__)


class Bridge:
    def __init__(self, model_pv_prefix, input_variables):
        self._mapping = None

        self._model_pv_prefix = model_pv_prefix
        self._input_variables = input_variables.values()
        self._process_mapping()

    def _process_mapping(self):
        """Creates the needed PVs and associated callbacks"""

        self._mapping = collections.defaultdict(dict)



        for variable in self._input_variables:
            pvname = variable.name

            self._mapping[pvname]['accl_pv'] = epics.PV(
                pvname, callback=self._process_pv
            )
            self._mapping[pvname]['model_pv'] = epics.PV(
                f'{self._model_pv_prefix}{pvname}'
            )

    def _process_pv(self, pvname, value, *args, **kwargs):
        """
        Callback to be executed when the real accelerator PV changes.
        Parameters
        ----------
        pvname : str
            The PV name
        value : object
            The PV value
        args : list
            Additional arguments passed
        kwargs : dict
            Additional keyword arguments passed
        """
        if value is None:
            return
        mapping = self._mapping[pvname]
        model_pv = mapping['model_pv']
        thread = threading.Thread(target=self._dispatch,
                                  args=(model_pv, value))
        thread.start()

    def _dispatch(self, model_pv, model_value):
        """
        Internal method invoked in a thread to execute the PUT operation since
        we can't do PUT operations inside of EPICS callbacks.
        Parameters
        ----------
        model_pv : str
            The model pv name
        model_value : object
            The value to write into `model_pv`
        """
        if not model_pv.connected:
            logger.debug(f'Skipping dispatch as model PV is disconnected: {model_pv}')
            return
        logger.debug(f'Writing value: {model_value} into: {model_pv}')
        if model_value:
            model_pv.put(model_value)
        else:
            logger.debug(f"Cannont put None to {model_pv}.")


def launch(*, variable_filename, model_pv_prefix, log_level):
    """
    Main method of this application responsible for setting up a simple log
    handler and the bridge.
    This will run until terminated by the user.
    Parameters
    ----------
    mapping_file : str
        Path to the CSV file which maps model -> machine PVs.
    model_pv_prefix : str
        The prefix to be used when composing the model PV name.
    denylist : list
        Real machine PVs to be ignored when consuming the CSV file.
    log_level : str
        The level of verbosity to use for the logger (DEBUG, INFO, WARN, ERROR).
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    logger.info('Starting the Bridge to Live PVs')
    input_variables, _ = load_variables(variable_filename)
    bridge = Bridge(model_pv_prefix, input_variables)

    try:
        while True:
            epics.ca.poll()
    except KeyboardInterrupt:
        logger.info('Finishing Bridge...')
        pass
    logger.info('Done!')


def get_parser():
    """
    Returns the ArgumentParser for this command line application.
    Returns
    -------
    parser : ArgumentParser
    """
    proj_desc = "Surrogate Model Bridge To Live Machine"
    parser = argparse.ArgumentParser(description=proj_desc)

    parser.add_argument(
        '--variable_filename',
        help='Path to the pickled model variables',
        default='./files/model_variables.pickle',
        required=False
    )
    parser.add_argument(
        '--model_pv_prefix',
        help='The EPICS PV Prefix used by the model.',
        default='test:',
        required=False
    )
    parser.add_argument(
        '--log_level',
        help='Configure level of log display',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO'
    )
    return parser


def parse_arguments(*args, **kwargs):
    """
    Invokes the ArgumentParser provided by `get_parser` and returns the
    dictionary of configurations
    Returns
    -------
    dict
    """
    parser = get_parser()
    return parser.parse_args(*args, **kwargs)


def main():
    """
    Wrapper method to invoke the argument parser and launch the bridge
    """
    args = parse_arguments()
    kwargs = vars(args)
    launch(**kwargs)


if __name__ == "__main__":
    import os
    os.environ["EPICS_CA_NAME_SERVERS"]=f"localhost:{os.environ['CA_NAME_SERVER_PORT']}"
    main()