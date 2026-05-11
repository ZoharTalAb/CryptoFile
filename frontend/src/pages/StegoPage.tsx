import { useMemo, useState } from "react";
import {
  Download,
  FileKey2,
  ScanSearch,
  Upload,
  WandSparkles,
} from "lucide-react";
import {
  stegoService,
  type EmbedResponse,
  type StegoType,
} from "../features/stego/stego.service";

type ActiveMode = "embed" | "extract";

const stegoOptions: { value: StegoType; label: string; hint: string }[] = [
  { value: "image", label: "Image", hint: "PNG and image-based payload hiding" },
  { value: "audio", label: "Audio", hint: "Wave-based secure message embedding" },
  { value: "video", label: "Video", hint: "Frame-based hidden payload workflow" },
];

const UNSUPPORTED_TEXT_EXTENSIONS = ["txt", "md", "csv", "json", "log"];
const UNSUPPORTED_TEXT_MESSAGE =
  "Text-based steganography is no longer supported. Please use image, audio, or video files.";

function isUnsupportedTextFile(file: File) {
  const extension = file.name.split(".").pop()?.toLowerCase();
  return UNSUPPORTED_TEXT_EXTENSIONS.includes(extension ?? "");
}

function isSupportedMediaFile(file: File) {
  const extension = file.name.split(".").pop()?.toLowerCase();
  return [
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
    "bmp",
    "wav",
    "mp3",
    "ogg",
    "m4a",
    "aac",
    "mp4",
    "mov",
    "webm",
    "avi",
  ].includes(extension ?? "");
}


export function StegoPage() {
  const [activeMode, setActiveMode] = useState<ActiveMode>("embed");
  const [stegoType, setStegoType] = useState<StegoType>("image");

  const [embedFile, setEmbedFile] = useState<File | null>(null);
  const [extractFile, setExtractFile] = useState<File | null>(null);
  const [secretData, setSecretData] = useState("");

  const [embedLoading, setEmbedLoading] = useState(false);
  const [extractLoading, setExtractLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);

  const [embedError, setEmbedError] = useState("");
  const [extractError, setExtractError] = useState("");

  const [embedResult, setEmbedResult] = useState<EmbedResponse | null>(null);
  const [extractResult, setExtractResult] = useState("");

  const currentTypeMeta = useMemo(() => {
    return stegoOptions.find((option) => option.value === stegoType);
  }, [stegoType]);

  async function handleEmbedSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setEmbedError("");
    setEmbedResult(null);

    if (!embedFile) {
      setEmbedError("Please choose a file to embed into");
      return;
    }

    if (isUnsupportedTextFile(embedFile)) {
      setEmbedError(UNSUPPORTED_TEXT_MESSAGE);
      return;
    }

    if (!isSupportedMediaFile(embedFile)) {
      setEmbedError("Unsupported file type. Please use image, audio, or video files.");
      return;
    }

    if (!secretData.trim()) {
      setEmbedError("Please enter the secret message you want to hide");
      return;
    }

    try {
      setEmbedLoading(true);

      const result = await stegoService.embedFile({
        stegoType,
        secretData: secretData.trim(),
        file: embedFile,
      });

      setEmbedResult(result);
      setSecretData("");
      setEmbedFile(null);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to embed message";
      setEmbedError(message);
    } finally {
      setEmbedLoading(false);
    }
  }

  async function handleExtractSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setExtractError("");
    setExtractResult("");

    if (!extractFile) {
      setExtractError("Please choose a file to extract from");
      return;
    }

    if (isUnsupportedTextFile(extractFile)) {
      setExtractError(UNSUPPORTED_TEXT_MESSAGE);
      return;
    }

    if (!isSupportedMediaFile(extractFile)) {
      setExtractError("Unsupported file type. Please use image, audio, or video files.");
      return;
    }

    try {
      setExtractLoading(true);

      const result = await stegoService.extractFile({
        stegoType,
        file: extractFile,
      });

      setExtractResult(result.extracted_message);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to extract message";
      setExtractError(message);
    } finally {
      setExtractLoading(false);
    }
  }

  async function handleDownloadCreatedFile() {
    if (!embedResult) return;

    try {
      setEmbedError("");
      setDownloadLoading(true);
      await stegoService.downloadCreatedFile(embedResult.file_id, embedResult.filename);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to download file";
      setEmbedError(message);
    } finally {
      setDownloadLoading(false);
    }
  }

  return (
    <div className="stego-page">
      <div className="stego-page__header">
        <div>
          <p className="section-eyebrow">Stego Lab</p>
          <h1 className="section-title">Embed and Extract</h1>
          <p className="section-text">
            Create protected steganography assets or extract hidden content from
            supported media.
          </p>
        </div>
      </div>

      <div className="stego-hero-grid">
        <article className="stego-hero-card">
          <div className="stego-hero-card__icon">
            <WandSparkles size={18} />
          </div>
          <span className="stego-hero-card__label">Current mode</span>
          <strong className="stego-hero-card__value">
            {activeMode === "embed" ? "Embed" : "Extract"}
          </strong>
        </article>

        <article className="stego-hero-card">
          <div className="stego-hero-card__icon">
            <FileKey2 size={18} />
          </div>
          <span className="stego-hero-card__label">Selected media</span>
          <strong className="stego-hero-card__value">{currentTypeMeta?.label}</strong>
        </article>
      </div>

      <div className="stego-panel">
        <div className="stego-panel__top">
          <div className="stego-mode-tabs">
            <button
              className={`stego-mode-tab ${
                activeMode === "embed" ? "stego-mode-tab--active" : ""
              }`}
              onClick={() => setActiveMode("embed")}
              type="button"
            >
              Embed
            </button>
            <button
              className={`stego-mode-tab ${
                activeMode === "extract" ? "stego-mode-tab--active" : ""
              }`}
              onClick={() => setActiveMode("extract")}
              type="button"
            >
              Extract
            </button>
          </div>

          <div className="stego-type-grid">
            {stegoOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`stego-type-card ${
                  stegoType === option.value ? "stego-type-card--active" : ""
                }`}
                onClick={() => setStegoType(option.value)}
              >
                <strong>{option.label}</strong>
                <span>{option.hint}</span>
              </button>
            ))}
          </div>
        </div>

        {activeMode === "embed" ? (
          <form className="stego-form" onSubmit={handleEmbedSubmit}>
            <div className="stego-form__grid">
              <label className="auth-label">
                <span>Carrier file</span>

                <div className="upload-box">
                  <input
                    type="file"
                    accept="image/*,audio/*,video/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0] ?? null;

                      if (!file) {
                        setEmbedFile(null);
                        return;
                      }

                      if (isUnsupportedTextFile(file)) {
                        setEmbedError(UNSUPPORTED_TEXT_MESSAGE);
                        setEmbedFile(null);
                        e.currentTarget.value = "";
                        return;
                      }

                      if (!isSupportedMediaFile(file)) {
                        setEmbedError("Unsupported file type. Please use image, audio, or video files.");
                        setEmbedFile(null);
                        e.currentTarget.value = "";
                        return;
                      }

                      setEmbedError("");
                      setEmbedFile(file);
                    }}
                    className="upload-box__input"
                  />

                  <div className="upload-box__content">
                    <Upload size={20} />
                    <p>
                      {embedFile
                        ? embedFile.name
                        : "Click to choose a file or drag it here"}
                    </p>
                  </div>
                </div>
              </label>

              <label className="auth-label">
                <span>Secret message</span>
                <textarea
                  className="stego-textarea"
                  placeholder="Write the secret content you want to hide..."
                  value={secretData}
                  onChange={(e) => setSecretData(e.target.value)}
                  rows={7}
                />
              </label>
            </div>

            {embedError ? (
              <div className="auth-alert auth-alert--error">{embedError}</div>
            ) : null}

            <div className="stego-form__actions">
              <button
                className="button button--primary"
                type="submit"
                disabled={embedLoading}
              >
                {embedLoading ? "Embedding..." : "Create Stego File"}
              </button>
            </div>

            {embedResult ? (
              <div className="stego-result-card">
                <div className="stego-result-card__header">
                  <div>
                    <p className="section-eyebrow">Embed complete</p>
                    <h3>Protected file created successfully</h3>
                  </div>
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => void handleDownloadCreatedFile()}
                    disabled={downloadLoading}
                  >
                    <Download size={16} />
                    {downloadLoading ? "Downloading..." : "Download"}
                  </button>
                </div>

                <div className="stego-result-grid">
                  <div className="stego-result-item">
                    <span>File ID</span>
                    <strong>{embedResult.file_id}</strong>
                  </div>
                  <div className="stego-result-item">
                    <span>Original filename</span>
                    <strong>{embedResult.original_filename}</strong>
                  </div>
                  <div className="stego-result-item">
                    <span>Stored filename</span>
                    <strong>{embedResult.filename}</strong>
                  </div>
                  <div className="stego-result-item">
                    <span>Stego type</span>
                    <strong>{embedResult.stego_type}</strong>
                  </div>
                </div>
              </div>
            ) : null}
          </form>
        ) : (
          <form className="stego-form" onSubmit={handleExtractSubmit}>
            <div className="stego-form__grid">
              <label className="auth-label">
                <span>Stego file</span>

                <div className="upload-box">
                  <input
                    type="file"
                    accept="image/*,audio/*,video/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0] ?? null;

                      if (!file) {
                        setExtractFile(null);
                        return;
                      }

                      if (isUnsupportedTextFile(file)) {
                        setExtractError(UNSUPPORTED_TEXT_MESSAGE);
                        setExtractFile(null);
                        e.currentTarget.value = "";
                        return;
                      }

                      if (!isSupportedMediaFile(file)) {
                        setExtractError("Unsupported file type. Please use image, audio, or video files.");
                        setExtractFile(null);
                        e.currentTarget.value = "";
                        return;
                      }

                      setExtractError("");
                      setExtractFile(file);
                    }}
                    className="upload-box__input"
                  />

                  <div className="upload-box__content">
                    <Upload size={20} />
                    <p>
                      {extractFile
                        ? extractFile.name
                        : "Click to choose a file or drag it here"}
                    </p>
                  </div>
                </div>
              </label>

              <div className="stego-extract-preview">
                <div className="stego-extract-preview__icon">
                  <ScanSearch size={18} />
                </div>
                <h3>Extraction flow</h3>
                <p>
                  Upload a supported file and CryptoFile will attempt to recover
                  hidden payload content from it.
                </p>
              </div>
            </div>

            {extractError ? (
              <div className="auth-alert auth-alert--error">{extractError}</div>
            ) : null}

            <div className="stego-form__actions">
              <button
                className="button button--primary"
                type="submit"
                disabled={extractLoading}
              >
                {extractLoading ? "Extracting..." : "Extract Hidden Message"}
              </button>
            </div>

            {extractResult ? (
              <div className="stego-result-card">
                <div className="stego-result-card__header">
                  <div>
                    <p className="section-eyebrow">Extraction complete</p>
                    <h3>Recovered hidden content</h3>
                  </div>
                </div>

                <div className="stego-message-output">{extractResult}</div>
              </div>
            ) : null}
          </form>
        )}
      </div>
    </div>
  );
}