########################################
# 1️⃣ Namespace
########################################
apiVersion: v1
kind: Namespace
metadata:
  name: app

---
########################################
# 2️⃣ MongoDB Secret
########################################
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
  namespace: app
type: Opaque
stringData:
  username: admin
  password: password123

---
########################################
# 3️⃣ MongoDB Headless Service
########################################
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: app
spec:
  clusterIP: None
  selector:
    app: mongodb
  ports:
    - port: 27017

---
########################################
# 4️⃣ MongoDB StatefulSet
########################################
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: app
spec:
  serviceName: "mongodb"
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      automountServiceAccountToken: false
      containers:
        - name: mongodb
          image: mongo
          ports:
            - containerPort: 27017
          env:
            - name: MONGO_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: username
            - name: MONGO_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: password
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: false
            capabilities:
              drop: ["ALL"]
          volumeMounts:
            - name: mongodb-persistent-storage
              mountPath: /data/db
  volumeClaimTemplates:
    - metadata:
        name: mongodb-persistent-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 2Gi

---
########################################
# 5️⃣ NodeApp Deployment
########################################
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nodeapp
  namespace: app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nodeapp
  template:
    metadata:
      labels:
        app: nodeapp
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      automountServiceAccountToken: false
      containers:
        - name: nodeapp
          image: shailesh49/nodeapp:latest
          ports:
            - containerPort: 3000
          env:
            - name: MONGO_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: username
            - name: MONGO_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: password
            - name: MONGO_HOST
              value: mongodb.app.svc.cluster.local
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]

---
########################################
# 6️⃣ NodeApp Service
########################################
apiVersion: v1
kind: Service
metadata:
  name: nodeapp
  namespace: app
spec:
  type: ClusterIP
  selector:
    app: nodeapp
  ports:
    - port: 3000
      targetPort: 3000

---
########################################
# 7️⃣ Optional NetworkPolicy
########################################
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-traffic
  namespace: app
spec:
  podSelector:
    matchLabels:
      app: nodeapp
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: mongodb
      ports:
        - protocol: TCP
          port: 3000
