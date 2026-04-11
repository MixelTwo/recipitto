# syntax=docker/dockerfile:1

ARG NODE_VERSION=20.16.0
ARG PYTHON_VERSION=3.12

################################################################################
FROM node:${NODE_VERSION}-alpine AS build
WORKDIR /usr/src/app

RUN npm i typescript@5.6.2

# Copy the rest of the source files into the image.
COPY frontend .
RUN npx tsc

################################################################################
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt

COPY backend/ .
COPY --from=build /usr/src/app/wwwroot ./build

EXPOSE 5000

ENV DBPATH=storage/db/db.db

CMD ["gunicorn", "main:app", "--bind=0.0.0.0:5000"]
