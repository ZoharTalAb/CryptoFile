import { api } from "../../lib/api";

export type FileItem = {
  id: number;
  filename: string;
  created_at: string;
  is_owner: boolean;
  download_url: string;
};

export type FilesListResponse = {
  owned_files: FileItem[];
  shared_with_me: FileItem[];
};

export type ShareFilePayload = {
  file_id: number;
  target_email: string;
};

export type ShareFileResponse = {
  share_id: number;
  file_id: number;
  shared_with_email: string;
  status: string;
  created_at: string;
};

function extractErrorMessage(error: unknown): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof (error as any).response === "object"
  ) {
    const response = (error as any).response;
    const detail = response?.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
  }

  return "Something went wrong. Please try again.";
}

function triggerBrowserDownload(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export const filesService = {
  async listFiles(): Promise<FilesListResponse> {
    const response = await api.get<FilesListResponse>("/files/");
    return response.data;
  },

  async shareFile(payload: ShareFilePayload): Promise<ShareFileResponse> {
    try {
      const response = await api.post<ShareFileResponse>("/share/", payload);
      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async downloadFile(fileId: number, filename: string) {
    try {
      const response = await api.get(`/files/${fileId}/download`, {
        responseType: "blob",
      });

      triggerBrowserDownload(response.data, filename);
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },
};