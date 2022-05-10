def uniqueName = currentBuild.startTimeInMillis + 'collectinfo'
pipeline {
    agent any
    environment {
        PMP_TOKEN = credentials('pmp_token')
    }
    stages {
        stage('stash files') {
            steps {                 
                stash name: "tosdp", includes: ""
            }
        }
        stage('Move to SDPCDI') {
	        agent { label 'sdpcdi_agent' }
            options { skipDefaultCheckout() }
	        stages {
	            stage('Unstash'){
                    steps {
                        unstash name: "tosdp"
                        sh "ls -la"
                    }	                
	            }	         
                stage('Build container') {
                    steps {
                        sh "docker run -di --name c_${uniqueName} -e PMP_TOKEN=${PMP_TOKEN} harbor.sdp.net.nz/library/i-sdpbase"
                        // sh "docker cp 'find_mdm_fmg_devices.py' 'c_${uniqueName}:/app/find_mdm_fmg_devices.py'"
                        // sh "docker cp 'findf5diskuse.py' 'c_${uniqueName}:/app/findf5diskuse.py'"
                        // sh "docker cp 'findfortigateperf.py' 'c_${uniqueName}:/app/findfortigateperf.py'"
                        // sh "docker cp 'findproxiesinfo.py' 'c_${uniqueName}:/app/findproxiesinfo.py'"
                        // sh "docker cp 'findjuniperinfo.py' 'c_${uniqueName}:/app/findjuniperinfo.py'"
                        // sh "docker cp 'findfmgfazdata.py' 'c_${uniqueName}:/app/findfmgfazdata.py'"
                        sh "docker cp 'ansible' 'c_${uniqueName}:/app/ansible'"
                        
                    }
                }
                stage('Execute script') {
                    steps {
                        // 1st mdm and fmg
                        // sh "docker exec c_${uniqueName} python3 -u find_mdm_fmg_devices.py"
                        // sh "docker cp 'c_${uniqueName}:/app/mdm_fmg_devices.json' 'mdm_fmg_devices.json'"
                        // stash name: "tomaster", includes: "mdm_fmg_devices.json"
                        // 2nd f5 stuff
                        // sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/f5/get_system_info.yml"
                        // sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/f5/get_system_performance.yml"
                        // sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/f5/get_relevant_config.yml"
                        // sh "docker exec c_${uniqueName} python3 -u findf5diskuse.py"
                        // sh "docker cp 'c_${uniqueName}:/app/f5_devices.json' 'f5_devices.json'"
                        // stash name: "tomaster", includes: "f5_devices.json"
                        // 3rd fortigate stuff
                        // sh "docker exec c_${uniqueName} python3 -u findfortigateperf.py"
                        // sh "docker cp 'c_${uniqueName}:/app/fortig_devices.json' 'fortig_devices.json'"
                        // stash name: "tomaster", includes: "fortig_devices.json" 
                        // 4rd proxies
                        // sh "docker exec c_${uniqueName} python3 -u findproxiesinfo.py"
                        // sh "docker cp 'c_${uniqueName}:/app/proxy_devices.json' 'proxy_devices.json'"
                        // stash name: "tomaster", includes: "proxy_devices.json" 
                        // 5th juniper
                        // sh "docker exec c_${uniqueName} python3 -u findjuniperinfo.py"
                        // sh "docker cp 'c_${uniqueName}:/app/juniper_devices.json' 'juniper_devices.json'"
                        // stash name: "tomaster", includes: "juniper_devices.json"
                        // 6th checkpoint devices
                        // sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/managers/runcommand_ckp.yml"
                        // sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/firewalls/runcommand_ckp.yml"
                        // sh "docker cp 'c_${uniqueName}:/app/ckpm_devices.json' 'ckpm_devices.json'"
                        // stash name: "tomaster", includes: "ckpm_devices.json"
                        // 7th fortimanagers, faz, fortiportals
                        sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/managers/runcommand_fortidmz.yml"
                        // sh "docker exec c_${uniqueName} python3 -u findfmgfazdata.py"
                        sh "docker cp 'c_${uniqueName}:/app/fortim_devices.json' 'fortim_devices.json'"
                        stash name: "tomaster", includes: "fortim_devices.json"            
                    }
                }                                                   
            }
            post { 
                always { 
                    sh "docker rm c_${uniqueName} -f"
                }
            }
        }
        // stage('Execute jobs in master') {
        //     steps {       
        //         sh "docker run -di --name c_${uniqueName} -e PMP_TOKEN=${PMP_TOKEN} --dns 10.96.0.10 --dns-search default.svc.cluster.local --dns-search svc.cluster.local --dns-search cluster.local harbor.sdp.net.nz/library/i-sdpbase"
        //         sh "docker cp 'ansible' 'c_${uniqueName}:/app/ansible'"
        //         sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/managers/runcommand_fortidmz.yml"
        //     }
        // }         
        stage('get results') {
            steps {
                unstash name: "tomaster"         
                sh "ls -la"
                sh "docker run -di --name c_${uniqueName} -e PMP_TOKEN=${PMP_TOKEN} --dns 10.96.0.10 --dns-search default.svc.cluster.local --dns-search svc.cluster.local --dns-search cluster.local harbor.sdp.net.nz/library/i-sdpbase"
                sh "docker cp 'save_data.py' 'c_${uniqueName}:/app/save_data.py'"
                // sh "docker cp 'mdm_fmg_devices.json' 'c_${uniqueName}:/app/mdm_fmg_devices.json'"
                // sh "docker cp 'f5_devices.json' 'c_${uniqueName}:/app/f5_devices.json'"
                // sh "docker cp 'fortig_devices.json' 'c_${uniqueName}://app/fortig_devices.json'"
                // sh "docker cp 'proxy_devices.json' 'c_${uniqueName}:/app/proxy_devices.json'"
                // sh "docker cp 'juniper_devices.json' 'c_${uniqueName}:/app/juniper_devices.json'"
                // sh "docker cp 'ckpm_devices.json' 'c_${uniqueName}:/app/ckpm_devices.json'"
                sh "docker cp 'fortim_devices.json' 'c_${uniqueName}:/app/fortim_devices.json'"
                
                sh "docker exec c_${uniqueName} python3 -u save_data.py"

            }
        }        
    }
    post { 
        always { 
            sh "docker rm c_${uniqueName} -f"
            cleanWs()
        }
    }    
}