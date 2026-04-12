import { api } from "../../lib/api";

export type StegoType = "image" | "audio" | "text" | "video";

export type EmbedResponse = {
  file_id: number;
  filename: string;
  original_filename: string;
  stego_type: string;
  download_url: string;
  created_at: string;
};

export type ExtractResponse = {
  stego_type: string;
  extracted_message: string;
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

export const stegoService = {
  async embedFile(params: {
    stegoType: StegoType;
    secretData: string;
    file: File;
  }): Promise<EmbedResponse> {
    try {
      const formData = new FormData();
      formData.append("stego_type", params.stegoType);
      formData.append("secret_data", params.secretData);
      formData.append("file", params.file);

      const response = await api.post<EmbedResponse>("/stego/embed", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async extractFile(params: {
    stegoType: StegoType;
    file: File;
  }): Promise<ExtractResponse> {
    try {
      const formData = new FormData();
      formData.append("stego_type", params.stegoType);
      formData.append("file", params.file);

      const response = await api.post<ExtractResponse>("/stego/extract", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return response.data;
    } catch (error) {
      throw new Error(extractErrorMessage(error));
    }
  },

  async downloadCreatedFile(fileId: number, filename: string) {
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