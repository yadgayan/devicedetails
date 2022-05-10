def uniqueName = currentBuild.startTimeInMillis + 'f5vip'
pipeline {
    agent any
    environment {
        PMP_TOKEN = credentials('pmp_token')
    }
    parameters {
        string(name: 'vip', defaultValue: '', description: 'vip to find')
    }
    stages {
        stage('stash files') {
            steps {
                script {
                    if ( params.vip.isEmpty() ){
                        error "Not empty values allowed"
                    }
                }                 
                stash name: "my_stash", includes: ""
            }
        }
        stage('Move to SDPCDI') {
	        agent { label 'sdpcdi_agent' }
            options { skipDefaultCheckout() }
	        stages {
	            stage('Unstash'){
                    steps {
                        unstash name: "my_stash"
                        sh "ls -la"
                    }	                
	            }	         
                stage('Build container') {
                    steps {
                        sh "docker run -di --name c_${uniqueName} -e PMP_TOKEN=${PMP_TOKEN} harbor.sdp.net.nz/library/i-sdpbase"
                        sh "docker cp 'vipsummary.py' 'c_${uniqueName}:/app/vipsummary.py'"
                        sh "docker cp 'ansible' 'c_${uniqueName}:/app/ansible'"
                    }
                }

                stage('Dig F5') {
                    steps {
                        sh "docker exec c_${uniqueName} ansible-playbook --forks=1 -i ansible/inventory/sdp.inv ansible/f5/get_vip_data.yml --extra-vars 'vip=${params.vip}'"
                    }
                }                 
                stage('Summary') {
                    steps {
                        sh "docker exec c_${uniqueName} python3 -u vipsummary.py"
                    }
                }                                       
            }
            post { 
                always { 
                    sh "docker rm c_${uniqueName} -f"
                }
            }
        }
    } 
}