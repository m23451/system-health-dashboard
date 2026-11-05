# Reflection

## 1. Continuous Delivery or Continuous Deployment for a payment service

Continuous Delivery means every change that passes the automated checks is built, tested and left ready to release, but a person decides when it goes live. Continuous Deployment removes that decision, so every change that passes the pipeline reaches production automatically. In my project the pipeline deploys each build to staging, smoke tests it and checks that Prometheus can see it, then stops at the Jenkins approval gate. That gate is the only difference between the two models: removing it would make this pipeline Continuous Deployment.

For a payment service I would choose Continuous Delivery. A faulty release can lose or duplicate money, and the cost of that is much higher than the cost of a short wait for approval. Payments are also regulated, so an auditor will expect a record of who approved each change, and my gate records the approver's name in the console. The approval also lets the team avoid releasing during busy periods. I would still automate everything up to that point, and I would move towards Continuous Deployment only once there were strong safeguards such as canary releases, feature flags and automatic rollback.

## 2. The quickest insight during the incident drill, and what was missing

I did not carry out the incident drill, so I cannot honestly say which metric or log line gave me the quickest insight during an incident, and I have not seen the HighErrorRate alert fire. What I can describe is what my setup was designed to show. The Error rate % panel would show how large the problem is, and the Error logs panel, which filters the JSON logs for level ERROR, would show which endpoint failed and when the first error appeared. The Service status panel and the ServiceDown alert cover the case where the app stops responding altogether.

Several things are missing from my setup. There is no notification channel, because I did not set up Alertmanager, so an alert would only be visible if someone opened Prometheus or Grafana. The alert rules have not been tested against real failures, so I do not know whether the thresholds are sensible. There is also no tracing, so I could not follow a single request across services. If I repeated this work, I would run the drill first, so the dashboard and alerts were proven before I relied on them.

## 3. How metrics and logs complement each other

Metrics and logs answer different questions. Metrics are numbers aggregated over time, so they are cheap to store, quick to graph and good for spotting that something is wrong and how big it is. They cannot tell you why. Logs record individual events with detail, so they explain what happened, but they are hard to scan at volume and do not show a trend on their own.

In my project, the http_requests_total counter feeds the Request rate and Error rate % panels. If the error rate rose, that panel would tell me that a share of requests were returning 5xx and when it started. The application logs each request as a JSON line with the endpoint, method, status and level, and Promtail ships them to Loki with an environment label. Filtering the Error logs panel for level ERROR would then show which endpoint was failing and on which environment. Using both, the metric makes me look and the log tells me where. The shared environment label also lets me switch the dashboard between staging and production, so the same question can be asked of both.

## 4. The alert threshold I would tune before going live

I would tune the HighErrorRate alert, which fires when more than 5% of requests return 5xx over a two-minute window and stays pending for one minute. The trade-off is noise against missed incidents. A low threshold or short window catches problems quickly, but on a low-traffic service a single failed request can exceed 5%, so the alert would fire on harmless blips and people would learn to ignore it. A high threshold or long window gives fewer false alarms, but a real incident may run for several minutes before anyone is told, and some users get errors the whole time.

Before going live I would first measure normal traffic and error rates, then set the threshold relative to that baseline. I would add a minimum request rate condition so that very quiet periods do not trigger the alert, and I would use two levels, a warning at a lower rate and a critical alert at a higher rate. For a service where failures are costly, such as payments, I would favour sensitivity and accept more noise, but only after routing alerts to a notification channel.

## 5. The manual step that remains

The main manual step is starting each pipeline run: I click Build Now in Jenkins, so a push to GitHub does not trigger anything. I could automate this with a GitHub webhook or by polling the repository, and by using a multibranch pipeline so each branch and pull request is built automatically. Related manual work is setting up the environment itself: creating the Jenkins job through the web page, adding the Compose plugin to the Jenkins container, and reconnecting Jenkins to the shared Docker network whenever the container is recreated. Jenkins Configuration as Code and a single setup script would make that repeatable.

The other manual step is the production approval, which is deliberate. The risk there is that someone approves without checking, so I would reduce it rather than remove it. I would show the approver the test results, the staging smoke test output and the Prometheus status in the approval message, restrict who may approve, and keep the record of who approved each build. I would also keep the automatic rollback, so that a bad approval can be undone quickly if the production smoke test fails.
