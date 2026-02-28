pipeline {
  agent any

  environment {
    IMAGE = "thongvm/my-app"
    TAG   = "${env.BUILD_NUMBER}"
    NS    = "jenkins"
    POD   = "kaniko-${env.BUILD_NUMBER}"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Docker Build & Push with Kaniko') {
      steps {
        sh """#!/bin/bash
          set -euo pipefail

          echo "Using namespace: ${NS}"
          echo "Kaniko pod name: ${POD}"
          echo "Destination image: ${IMAGE}:${TAG}"

          # Cleanup old pod (if any)
          kubectl delete pod ${POD} -n ${NS} --ignore-not-found=true || true

          # Create Kaniko pod
          kubectl run ${POD} \\
            --image=gcr.io/kaniko-project/executor:latest \\
            --restart=Never \\
            --namespace=${NS} \\
            --overrides='{
              "spec": {
                "containers": [{
                  "name": "kaniko",
                  "image": "gcr.io/kaniko-project/executor:latest",
                  "args": [
                    "--dockerfile=Dockerfile",
                    "--context=git://github.com/Thongvm1111/app-repo",
                    "--destination=${IMAGE}:${TAG}"
                  ],
                  "volumeMounts": [{
                    "name": "dockerhub-secret",
                    "mountPath": "/kaniko/.docker"
                  }]
                }],
                "volumes": [{
                  "name": "dockerhub-secret",
                  "secret": {
                    "secretName": "dockerhub-secret",
                    "items": [{
                      "key": ".dockerconfigjson",
                      "path": "config.json"
                    }]
                  }
                }],
                "restartPolicy": "Never"
              }
            }'

          # Wait until pod finishes (Succeeded/Failed) or timeout
          phase=""
          for i in {1..90}; do
            phase=\$(kubectl get pod ${POD} -n ${NS} -o jsonpath='{.status.phase}' 2>/dev/null || true)
            echo "[\$i] phase=\$phase"
            if [[ "\$phase" == "Succeeded" || "\$phase" == "Failed" ]]; then
              break
            fi
            sleep 5
          done

          echo "Final phase: \$phase"

          # Always dump debug info (very important)
          echo "===== POD (wide) ====="
          kubectl get pod ${POD} -n ${NS} -o wide || true

          echo "===== DESCRIBE ====="
          kubectl describe pod ${POD} -n ${NS} || true

          echo "===== EVENTS (tail) ====="
          kubectl get events -n ${NS} --sort-by=.lastTimestamp | tail -n 80 || true

          echo "===== KANIKO LOGS (tail) ====="
          kubectl logs -n ${NS} ${POD} -c kaniko --tail=200 || true

          # Decide pass/fail
          if [[ "\$phase" != "Succeeded" ]]; then
            echo "Kaniko build failed or timed out. Keeping pod ${POD} for investigation."
            exit 1
          fi

          # Cleanup only on success (avoid losing evidence)
          kubectl delete pod ${POD} -n ${NS} || true
        """
      }
    }

    stage('Update GitOps Repo') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'github-token',
          usernameVariable: 'GIT_USER',
          passwordVariable: 'GIT_PASS'
        )]) {
          sh """#!/bin/bash
            set -euo pipefail

            rm -rf gitops-repo || true
            git clone https://\${GIT_USER}:\${GIT_PASS}@github.com/Thongvm1111/gitops-repo.git
            cd gitops-repo

            # Update image line (works if deployment.yaml has: image: thongvm/my-app:<tag>)
            sed -i "s|image: ${IMAGE}:.*|image: ${IMAGE}:${TAG}|g" deployment.yaml

            git config user.email "jenkins@ci.com"
            git config user.name "Jenkins"

            git add deployment.yaml
            git diff --cached --quiet && { echo "No changes to commit."; exit 0; }

            git commit -m "Update image to ${TAG}"
            git push
          """
        }
      }
    }
  }
}
