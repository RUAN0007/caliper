import sys
import json

def main():
  if len(sys.argv) <= 1:
    print "python process-endorser.py <path/to/peer/log> [path/to/output/json]"
    return

  peer_log_path = sys.argv[1]
  
  e2e = {}
  preprocess = {}
  simulate = {}
  endorse = {}
  call = {}
  policy = {}
  with open(peer_log_path) as f:
    for line in f:
        if "E2E Txn" in line:
            token = line.split()
            latency = int(token[-5])
            txID = token[-8][1:-1]
            e2e[txID] = latency
        if "Preprocess txn" in line:
            token = line.split()
            latency = int(token[-2][1:-1])
            txID = token[-4][1:-1]
            preprocess[txID] = latency
        if "Simulate txn" in line:
            token = line.split() 
            latency = int(token[-2])
            txID = token[-4][1:-1]
            simulate[txID] = latency
        if "Endorse txn" in line:
            token = line.split()
            latency = int(token[-2])
            txID = token[-4][1:-1]
            endorse[txID] = latency
        if "Exit chaincode" in line:
            token = line.split()
            latency = int(token[-2][1:])
            txID = token[-6][1:-1]
            call[txID]=latency
        if "Check Policy Txn " in line:
            token = line.split()
            latency = int(token[-2])
            txID = token[-4][1:-1]
            policy[txID] = latency

  output_stats(e2e, preprocess, simulate, endorse, call, policy)

  if len(sys.argv) == 3:
    output_detail_json(e2e, preprocess, simulate, endorse, call, policy)


def mean(l):
    return sum(l) / len(l)


def percentile(l, p):
    n = int(round(p * len(l) + 0.5))
    return l[n-1]

def output_stats(e2e, preprocess, simulate, endorse, call, policy):
    mean_info = {"e2e": mean(e2e.values())}
    mean_detail = {"preprocess": mean(preprocess.values()),
                   "simulate": {"total": mean(simulate.values()), 
                                "detail": {
                                   "policy": mean(policy.values()),
                                   "execution": mean(call.values())
                                  }},
                   "endorse": mean(endorse.values())}
    mean_info["detail"] = mean_detail

    p = 0.5
    median_info = {"e2e": percentile(e2e.values(), p)}
    median_detail = {"preprocess": percentile(preprocess.values(), p),
                   "simulate": {"total": percentile(simulate.values(), p), 
                                "detail": {
                                   "policy": percentile(policy.values(), p),
                                   "execution": percentile(call.values(), p)
                                  }},
                   "endorse": percentile(endorse.values(), p)}
    median_info["detail"] = median_detail

    p = 0.99
    percentile_info = {"e2e": percentile(e2e.values(), p)}
    percentile_detail = {"preprocess": percentile(preprocess.values(), p),
                   "simulate": {"total": percentile(simulate.values(), p), 
                                "detail": {
                                   "policy": percentile(policy.values(), p),
                                   "execution": percentile(call.values(), p)
                                  }},
                   "endorse": percentile(endorse.values(), p)}
    percentile_info["detail"] = percentile_detail
    
    stats = {"mean": mean_info, "median": median_info, "percentile99": percentile_info}
    print json.dumps(stats, indent=2)


def output_detail_json(e2e, preprocess, simulate, endorse, call, policy):
    endorse_detail = {}
    for txID, e2e_latency in e2e.iteritems():
        tx_info = {"e2e": e2e_latency}
        tx_detail = {"preprocess": preprocess[txID], 
                     "simulate": {"total": simulate[txID], "detail": {
                                    "policy": policy[txID],
                                    "execution": call[txID]
                                 }},
                     "endorse": endorse[txID]}
        tx_info["detail"] = tx_detail
        endorse_detail[txID] = tx_info
    
    with open(sys.argv[2], 'w') as f:
        json.dump(endorse_detail, f, indent=4)

#   print e2e
#   print preprocess
#   print simulate
    # print endorse
    # print call
    # print policy

main()