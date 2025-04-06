# Build from the repository root with 'docker buildx bake -f docker/bake.hcl'

variable "TAG" {
    default = "latest"
}
variable "REGISTRY" {
    default = ""
}

# Build all images by default by using a matrix in the 'default' target
target "default" {
    matrix = {
        tgt = ["django-server", "celery-worker", "nginx-with-static", "pre-commit", "pytest", "django-server-test"]
    }
    name = "${tgt}"
    context = "."
    dockerfile = "docker/Dockerfile"
    target = "${tgt}"
    tags = ["${REGISTRY}${tgt}:${TAG}"]
}
