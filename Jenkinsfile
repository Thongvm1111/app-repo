pipeline {
  agent any

  environment {
    IMAGE = "thongvm/my-app"
    TAG = "${env.BUILD_NUMBER}"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Docker Build & Push with Kaniko') {
      steps {
        sh """
          kubectl run kaniko-${TAG} \
            --image=gcr.io/kaniko-project/executor:latest \
            --restart=Never \
            --namespace=jenkins \
            --overrides='{
              "spec": {
                "containers": [{
                  "name": "kaniko",
                  "image": "gcr.io/kaniko-project/executor:latest",
                  "args": [
                    "--dockerfile=/workspace/Dockerfile",
                    "--context=git://github.com/Thongvm1111/app-repo#refs/heads/main",
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
            }' \
            --wait=true \
            --timeout=300s || true

          # Chờ pod chạy xong (Succeeded hoặc Failed)
          echo "Waiting for Kaniko pod to complete..."
          for i in \$(seq 1 60); do
            STATUS=\$(kubectl get pod kaniko-${TAG} -n jenkins -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
            echo "Status: \$STATUS"
            if [ "\$STATUS" = "Succeeded" ] || [ "\$STATUS" = "Failed" ]; then
              break
            fi
            sleep 5
          done

          # In log của kaniko pod
          kubectl logs kaniko-${TAG} -n jenkins || true

          # Xóa pod sau khi xong
          kubectl delete pod kaniko-${TAG} -n jenkins || true

          if [ "\$STATUS" != "Succeeded" ]; then
            echo "Kaniko build failed!"
            exit 1
          fi
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
          sh """
            git clone https://${GIT_USER}:${GIT_PASS}@github.com/Thongvm1111/gitops-repo.git
            cd gitops-repo
            sed -i "s|image: ${IMAGE}:.*|image: ${IMAGE}:${TAG}|g" deployment.yaml
            git config user.email "jenkins@ci.com"
            git config user.name "Jenkins"
            git add .
            git commit -m "Update image to ${TAG}"
            git push
          """
        }
      }
    }

  }
}
