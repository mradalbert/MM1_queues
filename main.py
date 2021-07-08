import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

from libtopo import Queue


def stopTimeChooser():
    time = -1
    while time < 0:
        try:
            time = int(input("Set computation time limit[" + str(DEFAULT_STOP_TIME) + "]: ") or DEFAULT_STOP_TIME)
        except ValueError:
            continue
    return time


def lambdaChooser():
    _lambda = -1
    while _lambda < 0:
        try:
            _lambda = float(input("Set lambda[" + str(DEFAULT_LAMBDA) + "]: ") or DEFAULT_LAMBDA)
        except ValueError:
            continue
    return _lambda


def miChooser():
    mi = -1
    while mi < 0:
        try:
            mi = float(input("Set mi[" + str(DEFAULT_MI) + "]: ") or DEFAULT_MI)
        except ValueError:
            continue
    return mi


def modeChooser():
    mode = -1
    print("1: continuous mode")
    print("2: Server runs for 40 seconds and dies for 35 seconds repeatedly")
    while mode not in [1, 2]:
        mode = int(input("Set mode[1]: ") or 1)

    return mode


def generateServerDeathTime(current):
    return current + np.random.exponential(40, 1)


def generateServerResurrectonTime(current):
    return current + np.random.exponential(35, 1)


def runBreakingSimulation(queue, timeout):
    SERVER_ONLINE = 1
    NEXT_SERVER_STATE_CHANGE_TIME = 0
    temp = 0
    while queue.current_queue_time < timeout:
        if NEXT_SERVER_STATE_CHANGE_TIME <= queue.current_queue_time:
            if SERVER_ONLINE == 1:
                SERVER_ONLINE = 0
                NEXT_SERVER_STATE_CHANGE_TIME = generateServerResurrectonTime(NEXT_SERVER_STATE_CHANGE_TIME)
                temp = queue.next_request_time - queue.current_queue_time
            else:
                SERVER_ONLINE = 1
                NEXT_SERVER_STATE_CHANGE_TIME = generateServerDeathTime(NEXT_SERVER_STATE_CHANGE_TIME)
                queue.next_service_time = queue.current_queue_time + temp

        if SERVER_ONLINE:
            queue.make_step()
        else:
            queue.make_step_server_dead()


def runContinuousSimulation(queue, timeout):
    while queue.current_queue_time < timeout:
        queue.make_step()


if __name__ == '__main__':

    # initialize defaults
    DEFAULT_STOP_TIME = 500
    DEFAULT_MI = 8
    DEFAULT_LAMBDA = 1

    stop_time = stopTimeChooser()
    mi = miChooser()
    # mode = modeChooser()
    results = []
    processed_results = [list(), list(), list(), list()]

    lambdas = np.linspace(0.5, 6, 56)
    for lamb in lambdas:
        print("Compute lambda " + str(lamb))
        res = []
        for i in range(50):
            queue = Queue(lamb, mi)
            runBreakingSimulation(queue, stop_time)

            warmup = int(len(queue.results) * 2 / 10)
            res.append(np.average(queue.results[-warmup:]))

        results.append(res)

    for i, arr in enumerate(results):
        processed_results[1].append(np.average(arr))
        temp1, temp2 = st.t.interval(alpha=0.95, df=len(arr) - 1, loc=np.mean(arr), scale=st.sem(arr))
        processed_results[0].append(temp1)
        processed_results[2].append(temp2)
        pprim = lambdas[i] / mi / (40 / 75)
        a = (pprim + lambdas[i] * 35 * 35 / 75) / (1 - pprim) / lambdas[i]
        if a < 0:
            a = 25000  # 1060
        processed_results[3].append(a)

    plt.plot(lambdas, processed_results[0], linewidth='0.5', label="Dolny przedział ufności 95%")
    plt.plot(lambdas, processed_results[1], linewidth='1', label="Wynik symulacji")
    plt.plot(lambdas, processed_results[2], linewidth='0.5', label="Górny przedział ufności 95%")
    plt.plot(lambdas, processed_results[3], linewidth='1', label="Wynik obliczony analitycznie")
    plt.xlabel("λ [1/s")
    plt.ylabel("Średni czas obsługi żądania [s]")
    plt.legend()
    plt.yscale('log')
    plt.grid(True)
    plt.savefig("przerywany.png", dpi=600)
    plt.clf()

    results = []
    processed_results = [list(), list(), list(), list()]

    lambdas = np.linspace(0.5, 6, 56)
    for lamb in lambdas:
        print("Compute lambda " + str(lamb))
        res = []
        for i in range(50):
            queue = Queue(lamb, mi)
            runContinuousSimulation(queue, stop_time)

            warmup = int(len(queue.results) * 2 / 10)
            res.append(np.average(queue.results[-warmup:]))

        results.append(res)

    for i, arr in enumerate(results):
        processed_results[1].append(np.average(arr))
        temp1, temp2 = st.t.interval(alpha=0.95, df=len(arr) - 1, loc=np.mean(arr), scale=st.sem(arr))
        processed_results[0].append(temp1)
        processed_results[2].append(temp2)
        pprim = lambdas[i] / mi
        processed_results[3].append(pprim / (1 - pprim) / lambdas[i])

    plt.plot(lambdas, processed_results[0], linewidth='0.5', label="Dolny przedział ufności 95%")
    plt.plot(lambdas, processed_results[1], linewidth='1', label="Wynik symulacji")
    plt.plot(lambdas, processed_results[2], linewidth='0.5', label="Górny przedział ufności 95%")
    plt.plot(lambdas, processed_results[3], linewidth='1', label="Wynik obliczony analitycznie")
    plt.xlabel("λ [1/s]")
    plt.ylabel("Średni czas obsługi żądania [s]")
    plt.legend()
    plt.yscale('log')
    plt.grid(True)
    plt.savefig("nieprzerywany.png", dpi=600)
