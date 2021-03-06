import sys,time,os
import subprocess
from threading import Thread
import GeqeAPI
import geqeconf as conf
import json
import platform

print '\nproject root: ',conf.PROJECT_ROOT_PATH
print 'looback url: ',conf.LOOPBACK_SERVICE
print 'spark-submit: ',conf.SPARK_SUBMIT_PATH
print '--py-files: ',conf.PY_FILES
if conf.PROJECT_ROOT_PATH is None or conf.PROJECT_ROOT_PATH == '' or conf.PROJECT_ROOT_PATH[0] == '.':
    raise ValueError("You mest set PROJECT_ROOT_PATH in geqeconf.py to the full system path of the root project.")
os.chdir(conf.PROJECT_ROOT_PATH)


"""

Long running job to wait for and launch spark jobs for the geqe web app.

Usage:
python GeqeConsumer.py

"""


class JobRunner(Thread):

    def __init__(self,serviceUrl):
        super(JobRunner,self).__init__()
        self.url = serviceUrl
        self.service = GeqeAPI.GeqeRestHelper(self.url)


    def run(self):
        while True:
            job = self.getJob()

            # fail the job if we can't pull the associated data
            try:
                dataset = self.getDataset(job)
                if 'geqeModelId' not in job: polygon = self.getPolygon(job)
            except:
                self.setJobStatus(job, 'FAILED')
                raise

            self.setJobStatus(job, 'ACCEPTED')
            print 'JOB ACCEPTED ', job
            success = self.executeJob(job)
            if not success:
                self.setJobStatus(job, 'FAILED')


    def getJob(self):
        print 'Waiting for job.'
        while True:
            try:
                (status,job) = service.getNextJob()
            except:
                print 'Lost connection to ',self.url
                time.sleep(60)
                continue
            if status == 404:
                # no jobs found in WAITING state
                time.sleep(conf.WAIT_TIME)
                continue
            if status != 200:
               raise Exception('Error getting next job. status: '+str(status))
            return job

    def setJobStatus(self,job,status):
        job['status'] = status
        (status,data) = self.service.saveJob(job)
        if status != 200:
            raise Exception('Unable to save job. response code: '+str(status))
        return job



    def getDataset(self,job):
        (status,dataset) = self.service.getDatasetByName(job['datasetId'])
        if status != 200:
            raise Exception("Could not get get dataset for job. status: "+str(status))
        return dataset


    def getPolygon(self,job):
        (status,polygon) = self.service.getSiteListById(job['siteListId'])
        if status != 200:
            raise Exception("Could not get site list for job. status: "+str(status))
        return polygon



    def executeJob(self,job):
        print 'running job ',job

        stdoutFile = open('stdout.log','w')
        stderrFile = open('stderr.log','w')
        command = [conf.SPARK_SUBMIT_PATH]
        command.extend(conf.SPARK_OPTIONS)
        command.append('geqe-comm/GeqeRunner.py')
        if conf.ES_HOST is not None:
            command.extend(["--elasticsearchHost",conf.ES_HOST,"--elasticsearchPort",conf.ES_PORT])
        command.extend([self.service.serviceURL,job['id']])
        command = map(str,command)
        with open('lastcommand.sh','w') as handle:
            handle.write(' '.join(command))
        result = subprocess.call(command,stdout=stdoutFile,stderr=stderrFile)
        print 'result: ',str(result)
        stderrFile.close()
        stdoutFile.close()
        return int(result) == 0





if __name__ == '__main__':
    global CLUSTER_STATUS

    service = GeqeAPI.GeqeRestHelper(conf.LOOPBACK_SERVICE)

    (response,clusterStatus) = service.putStatus({'host': platform.node(), 'status':'RUNNING'})
    if response!= 200:
        print 'response: ',response
        print  clusterStatus
        raise Exception("Could not save cluster status.")


    thread = JobRunner(conf.LOOPBACK_SERVICE)
    thread.setDaemon(True)
    try:
        thread.start()
        while thread.isAlive():
            thread.join(sys.maxint)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    finally:
        service.deleteStatus(clusterStatus)
