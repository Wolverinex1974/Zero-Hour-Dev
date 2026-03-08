# ============================================================
# ZERO HOUR CORE: GITHUB ENGINE - v21.2
# ============================================================
# ROLE: Resilient Cloud Bridge (Iron Bridge Protocol)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# ============================================================
# PHASE 20: CACHE-BUSTER & CDN BYPASS
# UPDATE: Injected timestamp query parameters to force fresh
#         file downloads, bypassing the 5-minute GitHub delay.
# FIX: 100% Bracket-Free payload to defeat parser corruption.
# ============================================================

import os
import requests
import json
import time
import base64
import logging
import re
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger("Paradoxal")

class GitHubEngine:
    """
    The Iron Bridge: Manages all binary and metadata traffic
    between the Admin Suite and the GitHub Cloud Warehouse.
    """
    def __init__(self, secrets_path):
        """
        Initializes the engine with session-level resilience.
        """
        # Load Secrets
        if os.path.exists(secrets_path):
            with open(secrets_path, "r", encoding="utf-8") as f:
                secrets_data = json.load(f)
        else:
            secrets_data = dict()

        self.token = secrets_data.get("github_token", "")
        self.global_default_repo = secrets_data.get("github_repo", "")

        self.active_repo = self.global_default_repo
        self.session = requests.Session()

        # Retry Logic for Flaky Connections
        status_list = list((429, 500, 502, 503, 504))

        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=status_list
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

        # Headers
        headers_dict = dict()
        if self.token:
            headers_dict.update({"Authorization": f"token {self.token}"})
        headers_dict.update({"Accept": "application/vnd.github.v3+json"})
        self.session.headers.update(headers_dict)

        self.release_id = None
        self.refresh_release_info()

    def get_user_info(self):
        """
        PHASE 15: Validates API token and fetches authenticated user details.
        Includes Phase 20 Cache-Buster.
        """
        try:
            timestamp = int(time.time())
            url = f"https://api.github.com/user?t={timestamp}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                log.error(f" User Info failed with status {response.status_code}: {response.text}")
                return None

        except Exception as e:
            log.error(f" Exception fetching user info: {str(e)}")
            return None

    def _normalize(self, name):
        """
        Internal Helper: Mimics GitHub's internal filename sanitization.
        Rewritten with chr() to guarantee AI parser immunity.
        chr(91) is Left Bracket, chr(93) is Right Bracket.
        """
        clean_name = name.lower()
        clean_name = clean_name.replace("(", ".")
        clean_name = clean_name.replace(")", ".")
        clean_name = clean_name.replace(chr(91), ".")
        clean_name = clean_name.replace(chr(93), ".")
        clean_name = clean_name.replace(" ", ".")

        # Reduce multiple dots to a single dot
        while ".." in clean_name:
            clean_name = clean_name.replace("..", ".")

        clean_name = clean_name.strip(".")
        return clean_name

    def set_target_repo(self, repo_name):
        """
        Sovereign Context Switch: Swaps the engine's focus
        to a specific profile's mod repository.
        """
        if repo_name:
            if repo_name.strip():
                self.active_repo = repo_name.strip()
            else:
                self.active_repo = self.global_default_repo
        else:
            self.active_repo = self.global_default_repo

        log.info(f" Switched Warehouse: {self.active_repo}")
        self.refresh_release_info()

    def refresh_release_info(self):
        """
        Identifies the Warehouse Release ID for the active repo.
        PHASE 20: Adds Cache-Buster to ensure we see the LATEST release immediately.
        """
        timestamp = int(time.time())
        
        # Try 'v1' tag first
        url_v1 = f"https://api.github.com/repos/{self.active_repo}/releases/tags/v1?t={timestamp}"

        try:
            response = self.session.get(url_v1, timeout=10)

            if response.status_code == 200:
                release_data = response.json()
                self.release_id = release_data.get("id")
                log.info(f" Warehouse Verified: Tag v1 (ID: {self.release_id})")
                return

            # Fallback to 'latest'
            url_latest = f"https://api.github.com/repos/{self.active_repo}/releases/latest?t={timestamp}"

            response = self.session.get(url_latest, timeout=10)

            if response.status_code == 200:
                release_data = response.json()
                self.release_id = release_data.get("id")
                tag_name = release_data.get("tag_name", "Unknown")
                log.info(f" Warehouse Verified: {tag_name} (ID: {self.release_id})")
            else:
                log.error(f" No Release Warehouse found in {self.active_repo}.")
                self.release_id = None

        except Exception as e:
            log.error(f" Cloud Handshake Error: {str(e)}")
            self.release_id = None

    def get_release_assets(self):
        """
        CLOUD GARBAGE COLLECTOR:
        Retrieves a complete list of all binary zip assets currently
        hosted on the active GitHub Release.
        """
        if not self.release_id:
            self.refresh_release_info()
        if not self.release_id:
            return list()

        all_assets = list()
        current_page = 1
        timestamp = int(time.time())

        while True:
            list_url = f"https://api.github.com/repos/{self.active_repo}/releases/{self.release_id}/assets"

            params = dict()
            params.update({"per_page": 100})
            params.update({"page": current_page})
            # Cache Buster for asset list
            params.update({"t": timestamp})

            try:
                response = self.session.get(list_url, params=params, timeout=15)

                if response.status_code != 200:
                    break

                page_assets = response.json()

                if not page_assets:
                    break

                for asset in page_assets:
                    asset_data = dict()
                    asset_data.update({"id": asset.get("id")})
                    asset_data.update({"name": asset.get("name")})
                    asset_data.update({"size": asset.get("size")})
                    all_assets.append(asset_data)

                current_page = current_page + 1

            except Exception as e:
                log.error(f" Failed to fetch release assets: {str(e)}")
                break

        return all_assets

    def delete_release_asset(self, asset_id):
        """
        CLOUD GARBAGE COLLECTOR:
        Executes an atomic DELETE request to purge a specific asset from GitHub.
        """
        if not asset_id:
            return False

        delete_url = f"https://api.github.com/repos/{self.active_repo}/releases/assets/{asset_id}"

        try:
            response = self.session.delete(delete_url, timeout=15)

            if response.status_code == 204:
                return True
            else:
                log.error(f" Asset Delete Failed. Status Code: {response.status_code}")
                return False

        except Exception as e:
            log.error(f" Exception during asset deletion: {str(e)}")
            return False

    def delete_existing_asset(self, asset_name):
        """
        IRON BRIDGE DEEP SCAN:
        Scans every page of the release assets (100 per page) and uses
        normalized matching to bypass GitHub sanitization conflicts.
        """
        if not self.release_id:
            self.refresh_release_info()
        if not self.release_id:
            return False

        target_normalized = self._normalize(asset_name)

        current_page = 1
        found_asset_id = None
        found_asset_name = ""
        timestamp = int(time.time())

        while True:
            list_url = f"https://api.github.com/repos/{self.active_repo}/releases/{self.release_id}/assets"

            params = dict()
            params.update({"per_page": 100})
            params.update({"page": current_page})
            params.update({"t": timestamp})

            response = self.session.get(list_url, params=params)

            if response.status_code != 200:
                break

            assets_list = response.json()

            if not assets_list:
                break

            for asset in assets_list:
                warehouse_name = asset.get("name", "")
                warehouse_normalized = self._normalize(warehouse_name)

                if warehouse_normalized == target_normalized:
                    found_asset_id = asset.get("id")
                    found_asset_name = warehouse_name
                    break

            if found_asset_id:
                break

            current_page = current_page + 1

        if found_asset_id:
            delete_url = f"https://api.github.com/repos/{self.active_repo}/releases/assets/{found_asset_id}"

            delete_response = self.session.delete(delete_url)

            if delete_response.status_code == 204:
                log.info(f" Purged Collision: {found_asset_name}")
                time.sleep(2)
                return True

        return False

    def upload_mod_to_release(self, file_path):
        """
        IRON BRIDGE: Binary upload logic.
        Handles recursive purging and retry backoffs.
        """
        self.refresh_release_info()

        if not self.release_id:
            log.error(f" Upload failed: No valid Release ID for {self.active_repo}")
            return None

        filename = os.path.basename(file_path)
        encoded_name = quote(filename)

        upload_url = f"https://uploads.github.com/repos/{self.active_repo}/releases/{self.release_id}/assets?name={encoded_name}"

        attempt_count = 0
        max_attempts = 3

        while attempt_count < max_attempts:
            self.delete_existing_asset(filename)

            try:
                log.info(f" Initiating Binary Handoff: {filename}")

                headers_dict = dict()
                headers_dict.update({"Content-Type": "application/octet-stream"})

                with open(file_path, "rb") as binary_file:
                    upload_response = self.session.post(
                        upload_url,
                        data=binary_file,
                        headers=headers_dict,
                        timeout=None
                    )

                status = upload_response.status_code

                if status == 201:
                    log.info(f" Upload Successful: {filename}")
                    response_json = upload_response.json()
                    return response_json.get("browser_download_url")

                if status == 422:
                    log.warning(f" Sanitization collision detected for {filename}. Retrying...")
                    attempt_count = attempt_count + 1
                    time.sleep(3)
                else:
                    log.error(f" API Rejection: {status}")
                    attempt_count = attempt_count + 1
                    time.sleep(5)

            except Exception as e:
                log.error(f" Network/Forge Error: {str(e)}")
                attempt_count = attempt_count + 1
                time.sleep(5)

        return None

    def commit_file(self, local_path, commit_message):
        """
        THE ATOMIC COMMIT (PIPELINE COMPATIBLE)
        Reads any file (Binary/Text) -> Base64 -> GitHub API (PUT).
        Handles SHA verification for updates to prevent 409 Conflict.
        """
        if not os.path.exists(local_path):
            log.error(f" Commit failed: File not found {local_path}")
            return False

        filename = os.path.basename(local_path)
        remote_path = filename
        timestamp = int(time.time())

        url = f"https://api.github.com/repos/{self.active_repo}/contents/{remote_path}"

        sha = None
        try:
            # Check for existing file to get SHA (with cache buster)
            get_resp = self.session.get(f"{url}?t={timestamp}")
            if get_resp.status_code == 200:
                sha = get_resp.json().get("sha")
        except Exception as e:
            log.warning(f" SHA Lookup failed (assuming new file): {e}")

        try:
            with open(local_path, "rb") as f:
                content = f.read()

            b64_content = base64.b64encode(content).decode("utf-8")

            data = dict()
            data.update({"message": commit_message})
            data.update({"content": b64_content})
            data.update({"branch": "main"})

            if sha:
                data.update({"sha": sha})

            put_resp = self.session.put(url, json=data)

            success_codes = list((200, 201))
            if put_resp.status_code in success_codes:
                log.info(f" Commit Successful: {filename}")
                return True
            else:
                log.error(f" Commit Failed {put_resp.status_code}: {put_resp.text}")
                return False

        except Exception as e:
            log.error(f" Critical Commit Error: {e}")
            return False

    def commit_json(self, remote_path, json_data, commit_message):
        """
        PHASE 16 PREP: Direct JSON-to-Cloud sync.
        Bypasses the local hard drive entirely. Ideal for economy/store updates.
        """
        url = f"https://api.github.com/repos/{self.active_repo}/contents/{remote_path}"
        timestamp = int(time.time())

        sha = None
        try:
            get_resp = self.session.get(f"{url}?t={timestamp}")
            if get_resp.status_code == 200:
                sha = get_resp.json().get("sha")
        except Exception as e:
            log.warning(f" SHA Lookup failed for JSON (assuming new): {e}")

        try:
            json_string = json.dumps(json_data, indent=4)
            b64_content = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")

            data = dict()
            data.update({"message": commit_message})
            data.update({"content": b64_content})
            data.update({"branch": "main"})

            if sha:
                data.update({"sha": sha})

            put_resp = self.session.put(url, json=data)

            success_codes = list((200, 201))
            if put_resp.status_code in success_codes:
                log.info(f" JSON Commit Successful: {remote_path}")
                return True
            else:
                log.error(f" JSON Commit Failed {put_resp.status_code}: {put_resp.text}")
                return False

        except Exception as e:
            log.error(f" Critical JSON Commit Error: {e}")
            return False

    def upload_manifest_to_repo(self, local_path, remote_filename):
        """ Legacy Hook: Now redirects to the robust commit_file method. """
        return self.commit_file(local_path, f"Legacy Sync: {remote_filename}")

    def upload_software_to_repo(self, file_path, repo_alias, tag_name):
        """
        Software Publishing: Uploads binary builds (Launcher/Admin) to
        GitHub releases for public distribution.
        """
        timestamp = int(time.time())
        url_tag = f"https://api.github.com/repos/{repo_alias}/releases/tags/{tag_name}?t={timestamp}"

        try:
            resp = self.session.get(url_tag)

            if resp.status_code == 200:
                rel_id = resp.json().get("id")
            else:
                create_url = f"https://api.github.com/repos/{repo_alias}/releases"

                create_payload = dict()
                create_payload.update({"tag_name": tag_name})
                create_payload.update({"name": f"Build {tag_name}"})
                create_payload.update({"body": "Automated Software Distribution via Zero Hour."})
                create_payload.update({"draft": False})
                create_payload.update({"prerelease": False})

                create_resp = self.session.post(create_url, json=create_payload)
                if create_resp.status_code == 201:
                    rel_id = create_resp.json().get("id")
                else:
                    return None

            filename = os.path.basename(file_path)
            encoded_name = quote(filename)
            upload_url = f"https://uploads.github.com/repos/{repo_alias}/releases/{rel_id}/assets?name={encoded_name}"

            headers_dict = dict()
            headers_dict.update({"Content-Type": "application/octet-stream"})

            with open(file_path, "rb") as f:
                up_resp = self.session.post(
                    upload_url,
                    data=f,
                    headers=headers_dict
                )

            if up_resp.status_code == 201:
                return up_resp.json().get("browser_download_url")

        except Exception as e:
            log.error(f" Software Distro Failure: {str(e)}")

        return None