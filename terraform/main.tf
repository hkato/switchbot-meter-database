#
# Load secrets from SOPS encrypted dotenv file
#
data "sops_file" "secrets" {
  source_file = "../.env.sops"
  input_type  = "dotenv"
}

#
# SwitchBot API Token and Secret
#
resource "aws_ssm_parameter" "switchbot_token" {
  type  = "SecureString"
  name  = "/switchbot-meter-database/switchbot-token"
  value = data.sops_file.secrets.data.SWITCHBOT_TOKEN
}

resource "aws_ssm_parameter" "switchbot_secret" {
  type  = "SecureString"
  name  = "/switchbot-meter-database/switchbot-secret"
  value = data.sops_file.secrets.data.SWITCHBOT_SECRET
}

#
# Database configuration mongodb or influxdb
#
resource "aws_ssm_parameter" "database" {
  type  = "String"
  name  = "/switchbot-meter-database/database"
  value = data.sops_file.secrets.data.DATABASE
}

#
# MongoDB configuration
#
resource "aws_ssm_parameter" "mongodb_uri" {
  type  = "SecureString"
  name  = "/switchbot-meter-database/mongodb-uri"
  value = data.sops_file.secrets.data.MONGODB_URI

  count = aws_ssm_parameter.database.value == "mongodb" ? 1 : 0
}

resource "aws_ssm_parameter" "mongodb_database" {
  type  = "String"
  name  = "/switchbot-meter-database/mongodb-database"
  value = data.sops_file.secrets.data.MONGODB_DATABASE

  count = aws_ssm_parameter.database.value == "mongodb" ? 1 : 0
}

resource "aws_ssm_parameter" "mongodb_collection" {
  type  = "String"
  name  = "/switchbot-meter-database/mongodb-collection"
  value = data.sops_file.secrets.data.MONGODB_COLLECTION

  count = aws_ssm_parameter.database.value == "mongodb" ? 1 : 0
}

#
# InfluxDB configuration
#
resource "aws_ssm_parameter" "influxdb_url" {
  type  = "SecureString"
  name  = "/switchbot-meter-database/influxdb-url"
  value = data.sops_file.secrets.data.INFLUXDB_URL

  count = aws_ssm_parameter.database.value == "influxdb" ? 1 : 0
}

resource "aws_ssm_parameter" "influxdb_token" {
  type  = "SecureString"
  name  = "/switchbot-meter-database/influxdb-token"
  value = data.sops_file.secrets.data.INFLUXDB_TOKEN

  count = aws_ssm_parameter.database.value == "influxdb" ? 1 : 0
}

resource "aws_ssm_parameter" "influxdb_org" {
  type  = "String"
  name  = "/switchbot-meter-database/influxdb-org"
  value = data.sops_file.secrets.data.INFLUXDB_ORG

  count = aws_ssm_parameter.database.value == "influxdb" ? 1 : 0
}

resource "aws_ssm_parameter" "influxdb_bucket" {
  type  = "String"
  name  = "/switchbot-meter-database/influxdb-bucket"
  value = data.sops_file.secrets.data.INFLUXDB_BUCKET

  count = aws_ssm_parameter.database.value == "influxdb" ? 1 : 0
}
