#!/usr/bin/env python3

from web3 import Web3, HTTPProvider
import asyncio
import sys
from log import log
from logit_run import train_and_predict
from node import *
import time
import _thread
import os

rpc = 'https://dataseed1.phoenix.global/rpc/'
web3 = Web3(HTTPProvider(rpc))

abi='[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"previousAdmin","type":"address"},{"indexed":false,"internalType":"address","name":"newAdmin","type":"address"}],"name":"AdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"beacon","type":"address"}],"name":"BeaconUpgraded","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"jobId","type":"uint256"}],"name":"StartJob","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256[]","name":"userIds","type":"uint256[]"},{"indexed":false,"internalType":"uint256[]","name":"rewards","type":"uint256[]"},{"indexed":false,"internalType":"uint256","name":"jobId","type":"uint256"}],"name":"SubmitRewards","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"implementation","type":"address"}],"name":"Upgraded","type":"event"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"Phb","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"Rewards","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"getJobId","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_phb","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"proxiableUUID","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"startJob","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"userIds","type":"uint256[]"},{"internalType":"uint256[]","name":"rewards","type":"uint256[]"},{"internalType":"uint256","name":"jobId","type":"uint256"}],"name":"submitRewards","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"}],"name":"upgradeTo","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"upgradeToAndCall","outputs":[],"stateMutability":"payable","type":"function"}]'
abi = json.loads(abi)

contractAddress = '0xa1B190263A877c2B3fE8De351EeB720503967859'
phoenixNodesRewardsContract = web3.eth.contract(address=contractAddress, abi=abi)


class PhoenixNodeContract():
    def __init__(self, node_name, key):
        self.node_name = node_name
        self.key = key
        self.jobIdsWaitForStart = []

    def handle_event(self,event):
        eventStr = Web3.toJSON(event)
        print("event is ", eventStr)
        log(f"event is {eventStr}")

        dic = json.loads(eventStr)
        jobId = dic["args"]["jobId"]

        print("jobId is ",jobId)
        log(f'jobId is {jobId}')
        jobId = str(jobId)
        self.jobIdsWaitForStart.append(jobId)
        print("self.jobIdsWaitForStart is ", self.jobIdsWaitForStart)
        log(f'self.jobIdsWaitForStart is {self.jobIdsWaitForStart}')

    def startJob(self,jobId):
        train_files,computation_type = GetJobData(jobId,self.key,self.node_name)
        if len(train_files) == 0:
            print('get train files fail')
            log("get train files fail")
            return
        print("train_files is ",train_files)
        log(f'train_files is {train_files}')
        print("computation_type is ", computation_type)
        log(f'computation_type is {computation_type}')
        dict_r=train_and_predict(self.node_name,jobId,train_files)
        print("result of train_and_predict is ", dict_r)
        log(f'result of train_and_predict is {dict_r}')
        y_pred_path = dict_r["y_pred_path"]
        SubJobResult(jobId,self.key,self.node_name,computation_type,y_pred_path)
        print("Job end. JobId is ", jobId)
        log(f'Job end. JobId is {jobId}')

    async def log_loop(self,event_filter, poll_interval):
        while True:
            for PairCreated in event_filter.get_new_entries():
                self.handle_event(PairCreated)
            await asyncio.sleep(poll_interval)

    def eventMonitor(self):
        print("Begin start eventMonitor")
        log("Begin start eventMonitor")
        event_filter = phoenixNodesRewardsContract.events.StartJob.createFilter(fromBlock='latest')
        #event_filter = phoenixNodesRewardsContract.events.StartJob().get_logs(fromBlock=web3.eth.block_number)

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop(event_filter, 5)))
        finally:
            loop.close()

    def runJobsLoop(self, poll_interval):
        print("Begin start runJobsLoop")
        log("Begin start runJobsLoop")
        while True:
            if len(self.jobIdsWaitForStart)>0:
                print("len(self.jobIdsWaitForStart)>0,len(self.jobIdsWaitForStart) is ", len(self.jobIdsWaitForStart))
                log(f"len(self.jobIdsWaitForStart)>0,len(self.jobIdsWaitForStart) is {len(self.jobIdsWaitForStart)}")
                jobId=self.jobIdsWaitForStart[0]
                self.startJob(jobId)
                self.jobIdsWaitForStart.remove(jobId)
            time.sleep(poll_interval)

    def heartBeat(self, poll_interval):
        print("Begin start heartBeat")
        log("Begin start heartBeat")
        while True:
            result = HeartBeat(self.key, self.node_name)
            if result == 1:
                pass
            else:
                print("HeartBeat fail,please check out your local config and restart")
                log("HeartBeat fail,please check out your local config and restart")
                os._exit(0)
            time.sleep(poll_interval)

    def checkVersion(self):
        print("Check version")
        log("Check version")
        # result=CheckVersion(self.key,self.node_name)
        result = CheckVersion()
        if result == 1:
            print("Check version success")
            log("Check version success")
        else:
            print("Check version fail,please upgrade your local version")
            log("Check version fail,please upgrade your local version")
            sys.exit()


print("Phoenix node is ready")
log("Phoenix node is ready")
node_name = sys.argv[1]
node_name = node_name.replace("\"", "")
key = sys.argv[2]
key = key.replace("\"", "")
pContract=PhoenixNodeContract(node_name,key)
pContract.checkVersion()
_thread.start_new_thread(pContract.runJobsLoop, (2,))
_thread.start_new_thread(pContract.heartBeat, (1800,))
pContract.eventMonitor()

