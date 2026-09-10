{{- define "service-orders.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "service-orders.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- include "service-orders.name" . }}
{{- end }}
{{- end }}

{{- define "service-orders.labels" -}}
app.kubernetes.io/name: {{ include "service-orders.name" . }}
app.kubernetes.io/part-of: storefront
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{- define "service-orders.selectorLabels" -}}
app.kubernetes.io/name: {{ include "service-orders.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
