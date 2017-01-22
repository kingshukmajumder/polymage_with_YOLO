import logging

class polymage_logger:

    _init = False
    _default_log_level = None
    _default_modules = []
    _log_level_map = {}

    @classmethod
    def __init__(cls, _default_log_level=logging.INFO):

        cls._default_log_level = _default_log_level
        print("setting to default: ", cls._default_log_level)
        # if not yet initialized
        if cls._init == False:
            logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s")

            # init all the modules of PolyMage
            cls._init_default_modules()
            # set default log levels to default modules
            cls._assign_default_log_levels()

            # mark as initialized
            cls._init = True

        return

    @classmethod
    def _init_default_modules(cls):
        # create a list of all modules in PolyMage
        cls._default_modules.append("align_scale.py")
        cls._default_modules.append("bounds.py")
        cls._default_modules.append("cexpr.py")
        cls._default_modules.append("codegen.py")
        cls._default_modules.append("compiler.py")
        cls._default_modules.append("constructs.py")
        cls._default_modules.append("expr_ast.py")
        cls._default_modules.append("expression.py")
        cls._default_modules.append("expr_types.py")
        cls._default_modules.append("grouping.py")
        cls._default_modules.append("inline.py")
        cls._default_modules.append("libpluto.py")
        cls._default_modules.append("liveness.py")
        cls._default_modules.append("pipe.py")
        cls._default_modules.append("poly.py")
        cls._default_modules.append("poly_schedule.py")
        cls._default_modules.append("schedule.py")
        cls._default_modules.append("storage_mapping.py")
        cls._default_modules.append("targetc.py")
        cls._default_modules.append("tuner.py")

        return

    @classmethod
    def _assign_default_log_levels(cls):
        # assign default log levels to all default modules
        for module in cls._default_modules:
            cls._log_level_map[module] = cls._default_log_level

        return

    @classmethod
    def get_logger(cls, _module, _log_level=None):
        #
        # returns a logger for the 'module' and sets the specifed level (default
        # log level if not specified)
        #

        # assume default log level if not specified
        if _log_level == None:
            _log_level = cls._default_log_level

        # add entry for the module in log level map
        if _module not in cls._log_level_map:
            cls._log_level_map[_module] = _log_level

        # get logger from the logging module
        module_logger = logging.getLogger(_module)
        print(cls._log_level_map[_module])
        module_logger.setLevel(cls._log_level_map[_module])

        return module_logger
