class AppError(Exception):
    status_code = 500
    public_message = "Request failed."


class IngestError(AppError):
    status_code = 500
    public_message = "Indexing failed."


class MissingFileError(IngestError):
    status_code = 400
    public_message = "A PDF file is required."


class InvalidContentTypeError(IngestError):
    status_code = 400
    public_message = "The file must be a PDF."


class EmptyFileError(IngestError):
    status_code = 400
    public_message = "The PDF file is empty."


class FileTooLargeError(IngestError):
    status_code = 413
    public_message = "The PDF exceeds the maximum upload size."


class InvalidPdfError(IngestError):
    status_code = 422
    public_message = "The file is not a valid PDF."


class EmptyPdfError(IngestError):
    status_code = 422
    public_message = "The PDF has no extractable text."


class MissingApiKeyError(IngestError):
    status_code = 503
    public_message = "Embeddings are not configured."


class EmbeddingProviderError(IngestError):
    status_code = 502
    public_message = "The embedding service failed."


class IndexingError(IngestError):
    status_code = 500
    public_message = "Indexing failed."


class EmptyQueryError(AppError):
    status_code = 400
    public_message = "A search query is required."


class InvalidTopKError(AppError):
    status_code = 400
    public_message = "top_k must be between 1 and 100."


class SearchFailedError(AppError):
    status_code = 500
    public_message = "Search failed."
