import multiprocessing


def processes_in_parallel(number_of_processes,
                          processes_load,
                          method_in_parallel, args):

    # number of processes
    processes = []

    while len(processes_load) > 0:

        for proc in processes:
            if proc.is_alive() is False:
                processes.remove(proc)

        if len(processes) < number_of_processes:

            load = processes_load[0]

            args_with_load = [load]
            args_with_load.extend(args)

            processes.append(multiprocessing.Process(
                target=method_in_parallel, args=(args_with_load,)))

            processes[-1].start()

            processes_load.remove(load)

    while len(processes) > 0:
        for proc in processes:
            if proc.is_alive() is False:
                processes.remove(proc)
