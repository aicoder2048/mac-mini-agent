import httpx

_transport = httpx.HTTPTransport(local_address="0.0.0.0")
_client = httpx.Client(transport=_transport)


def start_job(url: str, prompt: str) -> dict:
    """POST to url/job with prompt, returns response dict."""
    response = _client.post(f"{url}/job", json={"prompt": prompt})
    response.raise_for_status()
    return response.json()


def get_job(url: str, job_id: str) -> str:
    """GET url/job/{job_id}, returns YAML content."""
    response = _client.get(f"{url}/job/{job_id}")
    response.raise_for_status()
    return response.text


def list_jobs(url: str, archived: bool = False) -> str:
    """GET url/jobs, returns YAML content."""
    params = {"archived": "true"} if archived else {}
    response = _client.get(f"{url}/jobs", params=params)
    response.raise_for_status()
    return response.text


def clear_jobs(url: str) -> dict:
    """POST url/jobs/clear, returns response dict."""
    response = _client.post(f"{url}/jobs/clear")
    response.raise_for_status()
    return response.json()


def latest_jobs(url: str, n: int = 1) -> str:
    """GET the full details of the latest N jobs."""
    import yaml

    response = _client.get(f"{url}/jobs")
    response.raise_for_status()
    data = yaml.safe_load(response.text)
    jobs = data.get("jobs") or []
    # Jobs are sorted by file order; take the last N (most recent)
    latest = jobs[-n:] if n < len(jobs) else jobs
    latest.reverse()  # Most recent first

    parts = []
    for job in latest:
        job_id = job["id"]
        detail = _client.get(f"{url}/job/{job_id}")
        detail.raise_for_status()
        parts.append(detail.text)
    return "---\n".join(parts)


def stop_job(url: str, job_id: str) -> dict:
    """DELETE url/job/{job_id}, returns response dict."""
    response = _client.delete(f"{url}/job/{job_id}")
    response.raise_for_status()
    return response.json()
