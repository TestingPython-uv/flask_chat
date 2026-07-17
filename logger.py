from colorama import init, Fore, Style

class Logger:
    def __init__(self, log_file: str | None = None):
        self.__log_file = log_file
        self.__logger_mode = True

        init()

    def log_info(self, info: str) -> None:
        if self.__logger_mode:
            if self.__log_file:
                with open(self.__log_file) as f:
                    f.write(f"[INFO]: {info}")
            else:
                print(Fore.GREEN + f"[INFO]: {info}" + Style.RESET_ALL)

    def log_error(self, error: str) -> None:
        if self.__logger_mode:
            if self.__log_file:
                with open(self.__log_file) as f:
                    f.write(f"[ERROR]: {error}")
            else:
                print(Fore.RED + f"[ERROR]: {error}" + Style.RESET_ALL)

    def disable_logger(self) -> None:
        self.__logger_mode = False

    def enable_logger(self) -> None:
        self.__logger_mode = True