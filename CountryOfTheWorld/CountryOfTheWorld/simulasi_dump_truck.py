import json
from datetime import time

import pandas
from mpmath import rand


def cdf(pdf):
    res = []
    commulative = 0
    for prob in pdf:
        commulative += prob
        res.append(commulative)
    return res


# Parameter input

# traveltime_variant = int(input('variant of travel time (Int)?'))
# traveltime = {'time': list(map(int, input('List of travel time (list)? ').strip().split()))[:traveltime_variant],
#               'pdf': list(map(float, input('List of travel time prob (List)? ').strip().split()))[:traveltime_variant]}
# loadingtime_variant = int(input('variant of loading time (Int)?'))
# loadingtime = {'time': list(map(int, input('List of loading time (List)? ').strip().split()))[:loadingtime_variant],
#                'pdf': list(map(float, input('List of loading time prob (List)? ').strip().split()))[
#                       :loadingtime_variant]}
# scalertime_variant = int(input('variant of loading time (Int)?'))
# scalertime = {'time': list(map(int, input('List of scaler time (List)? ').strip().split()))[:scalertime_variant],
#               'pdf': list(map(float, input('List of scaler time prob (List)? ').strip().split()))[:scalertime_variant]}
# kendaraan = int(input('How many vehicle today (Int)?'))
# active_loader = int(input('How many active loader today (Int)?'))
# active_scaler = int(input('How many active scaler today (Int)?'))
# str_start_time = input('Start time (hh:MM)?')
# start_split = regex.split(':', str_start_time)
# start_operating_time = time(hour=int(start_split[0]), minute=int(start_split[0]))
# str_end_time = input('End time (hh:MM)?')
# end_split = regex.split(':', str_end_time)
# end_operating_time = time(hour=int(end_split[0]), minute=int(end_split[0]))
# max_epoch = int(input('Max epoch (Int)?'))

traveltime = {'time': [40, 45, 50, 55, 60], 'pdf': [0.14, 0.22, 0.43, 0.17, 0.04]}
loadingtime = {'time': [10, 12, 14, 16, 18], 'pdf': [0.17, 0.3, 0.33, 0.16, 0.04]}
scalingtime = {'time': [2, 6, 10, 14, 18], 'pdf': [0.15, 0.35, 0.30, 0.1, 0.1]}
kendaraan = 6
active_loader = 2
active_scaler = 1
start_operating_time = time(hour=9, minute=0)
end_operating_time = time(hour=17, minute=0)
max_epoch = 100

traveltime['cdf'] = cdf(traveltime['pdf'])
loadingtime['cdf'] = cdf(loadingtime['pdf'])
scalingtime['cdf'] = cdf(scalingtime['pdf'])
FEL = []
ListOfDemandsToServe = []
loader = 0
scaler = 0
queue_loader = 0
queue_scaler = 0
busy_time_loader_epoch = []
busy_time_scaler_epoch = []


def time_add(t, delta):
    unixtime = t.hour * 3600 + t.minute * 60
    new_unix = unixtime + delta * 60
    return time(new_unix // 3600, (new_unix % 3600) // 60)


def event(*args):
    global loader
    global scaler
    global queue_loader
    global queue_scaler
    global ListOfQueueLoader
    global ListOfQueueScaler
    global kendaraan
    delay = {'loading': 0, 'scaling': 0}
    if args[0]['event_name'] == 'StartOperating':
        for vehicle in range(kendaraan):
            FEL.append({'event_name': 'Arrival', 'time': args[0]['time'], 'dump_truck': vehicle})

    elif args[0]['event_name'] == 'Arrival':
        pass
        if loader < active_loader:
            rand_loading_time = rand()
            loading_time = 0
            for cdf_scalingtime in loadingtime['cdf']:
                if cdf_scalingtime > rand_loading_time:
                    loading_time = loadingtime['time'][loadingtime['cdf'].index(cdf_scalingtime)]
                    break
            FEL.append({'event_name': 'EndOfLoading',
                        'time': time_add(args[0]['time'], loading_time),
                        'dump_truck': args[0]['dump_truck']})
            loader = loader + 1
        else:
            ListOfQueueLoader.append(args[0])
            queue_loader += 1
        delay = {'loading': 0, 'scaling': 0}
    elif args[0]['event_name'] == 'EndOfLoading':
        if scaler < active_scaler:
            rand_scaling_time = rand()
            scaling_time = 0
            for cdf_scalingtime in scalingtime['cdf']:
                if cdf_scalingtime > rand_scaling_time:
                    scaling_time = scalingtime['time'][scalingtime['cdf'].index(cdf_scalingtime)]
                    break
            FEL.append({'event_name': 'EndOfScaling',
                        'time': time_add(args[0]['time'], scaling_time),
                        'dump_truck': args[0]['dump_truck']})
            scaler = scaler + 1
        else:
            ListOfQueueScaler.append(args[0])
            queue_scaler += 1
        if len(ListOfQueueLoader) > 0:
            rand_loading_time = rand()
            loading_time = 0
            for cdf_loadingtime in loadingtime['cdf']:
                if cdf_loadingtime > rand_loading_time:
                    loading_time = loadingtime['time'][loadingtime['cdf'].index(cdf_loadingtime)]
                    break
            delay = {'loading': (args[0]['time'].hour * 60 + args[0]['time'].minute) -
                                (ListOfQueueLoader[0]['time'].hour * 60 + ListOfQueueLoader[0]['time'].minute),
                     'scaling': 0}
            FEL.append({'event_name': 'EndOfLoading',
                        'time': time_add(args[0]['time'], loading_time),
                        'dump_truck': ListOfQueueLoader[0]['dump_truck']})
            ListOfQueueLoader = ListOfQueueLoader[1:]
            queue_loader -= 1
        else:
            delay = {'loading': 0, 'scaling': 0}
            loader -= 1
    elif args[0]['event_name'] == 'EndOfScaling':
        if len(ListOfQueueScaler) > 0:
            rand_loading_time = rand()
            service_time = 0
            for cdf_interarrival in loadingtime['cdf']:
                if cdf_interarrival > rand_loading_time:
                    service_time = loadingtime['time'][loadingtime['cdf'].index(cdf_interarrival)]
                    break
            delay = {'loading': 0, 'scaling': (args[0]['time'].hour * 60 + args[0]['time'].minute) -
                                              (ListOfQueueScaler[0]['time'].hour * 60 + ListOfQueueScaler[0][
                                                  'time'].minute)}
            FEL.append({'event_name': 'EndOfScaling',
                        'time': time_add(args[0]['time'], service_time),
                        'dump_truck': ListOfQueueScaler[0]['dump_truck']})
            ListOfQueueScaler = ListOfQueueScaler[1:]
            queue_scaler -= 1
        else:
            delay = {'loading': 0, 'scaling': 0}
        rand_next_arrival = rand()
        next_traveltime = 0
        for cdf_traveltime in traveltime['cdf']:
            if cdf_traveltime > rand_next_arrival:
                next_traveltime = traveltime['time'][traveltime['cdf'].index(cdf_traveltime)]
                break
        FEL.append({'event_name': 'Arrival',
                    'time': time_add(args[0]['time'], next_traveltime),
                    'dump_truck': args[0]['dump_truck']})
        pass
    elif args[0]['event_name'] == 'EndOperating':
        delay = {'loading': 0, 'scaling': 0}
    FEL.remove(args[0])
    return delay


def get_next_event(events):
    min_time = events[0]['time']
    res = []
    for candidat in range(len(events)):
        if min_time > events[candidat]['time']:
            min_time = events[candidat]['time']
            res = [events[candidat]]
        elif min_time == events[candidat]['time']:
            res.append(events[candidat])
    return res, min_time


over_time_loader_epoch = []
utilization_loader_epoch = []
utilization_scaler_epoch = []
delay_loader_epoch = []
delay_scaler_epoch = []
ndelay_loader_epoch = []
ndelay_scaler_epoch = []
loading_queue_epoch = []
scaling_queue_epoch = []

logs = pandas.DataFrame(columns=[
    'epoch',
    't',
    'loader',
    'scaler',
    'queue_loader',
    'queue_scaler',
    'ListOfQueueLoader',
    'ListOfQueueScaler',
    'FEL',
    'busy_time_loader',
    'busy_time_scaler'
])

for epoch in range(max_epoch):
    t_now = start_operating_time
    busy_time_loader = 0
    busy_time_scaler = 0
    loader = 0
    scaler = 0
    queue_loader = 0
    queue_scaler = 0
    ListOfQueueLoader = []
    ListOfQueueScaler = []
    FEL = []
    delays = []
    loading_queues = []
    scaling_queues = []
    while t_now < end_operating_time:
        old_t = t_now
        log = [epoch]
        if len(FEL) == 0:
            busy_time_loader += loader * ((t_now.hour * 60 + t_now.minute) - (old_t.hour * 60 + old_t.minute))
            busy_time_scaler += scaler * ((t_now.hour * 60 + t_now.minute) - (old_t.hour * 60 + old_t.minute))
            log.append(t_now)
            FEL.append({'event_name': 'StartOperating', 'time': start_operating_time})
            FEL.append({'event_name': 'EndOperating', 'time': end_operating_time})
            log.append(loader)
            log.append(scaler)
            log.append(queue_loader)
            log.append(queue_scaler)
            log.append(str(ListOfQueueLoader))
            log.append(str(ListOfQueueScaler))
            log.append(str(FEL))
            log.append(busy_time_loader)
            log.append(busy_time_scaler)
            logs.loc[len(logs)] = log
        else:
            next_events, t_now = get_next_event(FEL)
            busy_time_loader += loader * ((t_now.hour * 60 + t_now.minute) - (old_t.hour * 60 + old_t.minute))
            busy_time_scaler += scaler * ((t_now.hour * 60 + t_now.minute) - (old_t.hour * 60 + old_t.minute))
            log.append(t_now)
            for next_event in next_events:
                delays.append(event(next_event))
            log.append(loader)
            log.append(scaler)
            log.append(queue_loader)
            log.append(queue_scaler)
            log.append(str(ListOfQueueLoader))
            log.append(str(ListOfQueueScaler))
            log.append(str(FEL))
            log.append(busy_time_loader)
            log.append(busy_time_scaler)
            logs.loc[len(logs)] = log
        loading_queues.append(queue_loader)
        scaling_queues.append(queue_scaler)

    sum_delay_loader = 0
    sum_delay_scaler = 0
    ndelay_loader = 0
    ndelay_scaler = 0
    for i in range(len(delays)):
        if delays[i]['loading'] > 0:
            sum_delay_loader += delays[i]['loading']
            ndelay_loader += 1
        if delays[i]['scaling'] > 0:
            sum_delay_scaler += delays[i]['scaling']
            ndelay_scaler += 1
    loading_queue_epoch.append(max(loading_queues))
    scaling_queue_epoch.append(max(scaling_queues))
    try:
        delay_loader_epoch.append(sum_delay_loader / float(ndelay_loader))
    except Exception:
        delay_loader_epoch.append(0)
    try:
        delay_scaler_epoch.append(sum_delay_scaler / float(ndelay_scaler))
    except Exception:
        delay_scaler_epoch.append(0)
    try:
        ndelay_loader_epoch.append(ndelay_loader / float(len(delays)))
    except Exception:
        ndelay_loader_epoch.append(0)
    try:
        ndelay_scaler_epoch.append(ndelay_scaler / float(len(delays)))
    except Exception:
        ndelay_scaler_epoch.append(0)
    busy_time_loader_epoch.append(busy_time_loader)
    busy_time_scaler_epoch.append(busy_time_scaler)
    utilization_loader_epoch.append(busy_time_loader /
                                    (((max(t_now, end_operating_time).hour * 60 + max(t_now,
                                                                                      end_operating_time).minute) -
                                      (start_operating_time.hour * 60 + start_operating_time.minute)) * float(
                                        active_loader)))
    utilization_scaler_epoch.append(busy_time_scaler /
                                    (((max(t_now, end_operating_time).hour * 60 + max(t_now,
                                                                                      end_operating_time).minute) -
                                      (start_operating_time.hour * 60 + start_operating_time.minute)) * float(
                                        active_scaler)))
# print(logs)

busy_time_loader_epoch = sorted(busy_time_loader_epoch)
over_time_loader_epoch = sorted(over_time_loader_epoch)
utilization_loader_epoch = sorted(utilization_loader_epoch)
delay_loader_epoch = sorted(delay_loader_epoch)
delay_scaler_epoch = sorted(delay_scaler_epoch)
ndelay_loader_epoch = sorted(ndelay_loader_epoch)
loading_queue_epoch = sorted(loading_queue_epoch)
avg_busy_time_loader = 0
avg_busy_time_scaler = 0
avg_utilization_loader = 0
avg_utilization_scaler = 0
avg_delay_loader = 0
avg_delay_scaler = 0
avg_ndelay_loader = 0
avg_ndelay_scaler = 0
avg_queue_loader = 0
avg_queue_scaler = 0
for i in range(len(busy_time_loader_epoch)):
    avg_busy_time_loader += busy_time_loader_epoch[i]
    avg_utilization_loader += utilization_loader_epoch[i]
    avg_delay_loader += delay_loader_epoch[i]
    avg_ndelay_loader += ndelay_loader_epoch[i]
    avg_queue_loader += loading_queue_epoch[i]
    avg_busy_time_scaler += busy_time_loader_epoch[i]
    avg_utilization_scaler += utilization_loader_epoch[i]
    avg_delay_scaler += delay_scaler_epoch[i]
    avg_ndelay_scaler += ndelay_scaler_epoch[i]
    avg_queue_scaler += scaling_queue_epoch[i]
avg_busy_time_loader /= float(active_loader * max_epoch)
avg_utilization_loader /= float(max_epoch)
avg_delay_loader /= float(max_epoch)
avg_ndelay_loader /= float(max_epoch)
avg_queue_loader /= float(max_epoch)
avg_busy_time_scaler /= float(active_scaler * max_epoch)
avg_utilization_scaler /= float(max_epoch)
avg_delay_scaler /= float(max_epoch)
avg_ndelay_scaler /= float(max_epoch)
avg_queue_scaler /= float(max_epoch)
print('active loader:', active_loader)
print('active scaler:', active_scaler)
print('epoch:', max_epoch)
print(json.dumps({
    'min_busy_time_loader': busy_time_loader_epoch[0] / float(active_loader),
    'median_busy_time_loader': busy_time_loader_epoch[int(len(busy_time_loader_epoch) / 2)] / float(active_loader),
    'mean_busy_time_loader': avg_busy_time_loader,
    'max_busy_time_loader': busy_time_loader_epoch[len(busy_time_loader_epoch) - 1] / float(active_loader)
}, indent=4))

print(json.dumps({
    'min_busy_time_scaler': busy_time_scaler_epoch[0] / float(active_scaler),
    'median_busy_time_scaler': busy_time_scaler_epoch[int(len(busy_time_scaler_epoch) / 2)] / float(active_scaler),
    'mean_busy_time_scaler': avg_busy_time_scaler,
    'max_busy_time_scaler': busy_time_scaler_epoch[len(busy_time_scaler_epoch) - 1] / float(active_scaler)
}, indent=4))

print(json.dumps({
    'min_utilization_loader': utilization_loader_epoch[0],
    'median_utilization_loader': utilization_loader_epoch[int(len(utilization_loader_epoch) / 2)],
    'mean_utilization_loader': avg_utilization_loader,
    'max_utilization_loader': utilization_loader_epoch[len(utilization_loader_epoch) - 1]
}, indent=4))

print(json.dumps({
    'min_utilization_scaler': utilization_scaler_epoch[0],
    'median_utilization_scaler': utilization_scaler_epoch[int(len(utilization_scaler_epoch) / 2)],
    'mean_utilization_scaler': avg_utilization_scaler,
    'max_utilization_scaler': utilization_scaler_epoch[len(utilization_scaler_epoch) - 1]
}, indent=4))

print(json.dumps({
    'min_delay_loader': delay_loader_epoch[0],
    'median_delay_loader': delay_loader_epoch[int(len(delay_loader_epoch) / 2)],
    'mean_delay_loader': avg_delay_loader,
    'max_delay_loader': delay_loader_epoch[len(delay_loader_epoch) - 1]
}, indent=4))

print(json.dumps({
    'min_ndelay_scaler': ndelay_scaler_epoch[0],
    'median_ndelay_scaler': ndelay_scaler_epoch[int(len(ndelay_scaler_epoch) / 2)],
    'mean_ndelay_scaler': avg_ndelay_scaler,
    'max_ndelay_scaler': ndelay_scaler_epoch[len(ndelay_scaler_epoch) - 1]
}, indent=4))

print(json.dumps({
    'min_queue_scaler': loading_queue_epoch[0],
    'median_queue_scaler': loading_queue_epoch[int(len(loading_queue_epoch) / 2)],
    'mean_queue_scaler': avg_queue_loader,
    'max_queue_scaler': loading_queue_epoch[len(loading_queue_epoch) - 1]
}, indent=4))

print(json.dumps({
    'min_queue_scaler': scaling_queue_epoch[0],
    'median_queue_scaler': scaling_queue_epoch[int(len(scaling_queue_epoch) / 2)],
    'mean_queue_scaler': avg_queue_scaler,
    'max_queue_scaler': scaling_queue_epoch[len(scaling_queue_epoch) - 1]
}, indent=4))

save = input('save log (y/n)?')
output_log = 'simulation_log.csv'
if save == 'y':
    logs.to_csv(output_log)
    print(output_log)
