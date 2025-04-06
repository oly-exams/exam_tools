# Build from the repository root with 'docker buildx bake -f docker/bake.hcl'

variable "TAG" {
    default = "latest"
}
variable "REGISTRY" {
    default = ""
}

group "default" {
    targets = ["django-server", "celery-worker", "nginx-with-static", "pre-commit", "pytest"]
}

target "django-server" {
    context = "."
    dockerfile = "docker/Dockerfile"
    target = "django-server"
    tags = ["${REGISTRY}django-server:${TAG}"]
}
target "celery-worker" {
    context = "."
    dockerfile = "docker/Dockerfile"
    target = "celery-worker"
    tags = ["${REGISTRY}celery-worker:${TAG}"]
}
target "nginx-with-static" {
    context = "."
    dockerfile = "docker/Dockerfile"
    target = "nginx-with-static"
    tags = ["${REGISTRY}nginx-with-static:${TAG}"]
}
target "pre-commit" {
    context = "."
    dockerfile = "docker/Dockerfile"
    target = "pre-commit"
    tags = ["${REGISTRY}pre-commit:${TAG}"]
}
target "pytest" {
    context = "."
    dockerfile = "docker/Dockerfile"
    target = "pytest"
    tags = ["${REGISTRY}pytest:${TAG}"]
}
target "django-server-test" {
    context = "."
    dockerfile = "docker/Dockerfile"
    target = "django-server-test"
    tags = ["${REGISTRY}django-server-test:${TAG}"]
}
