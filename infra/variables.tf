variable "location" {
  type    = string
  default = "southafricanorth"
}
variable "environment" {
  type    = string
  default = "dev"
}
variable "container_image" {
  type        = string
  description = "Immutable application image, preferably pinned by digest."
}
variable "owner" {
  type    = string
  default = "portfolio"
}
