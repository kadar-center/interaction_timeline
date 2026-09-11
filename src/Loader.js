// This module creates a full-screen loading overlay with a spinner and text.
// It exposes a global function `removeLoader()` that can be called to fade out
// and remove the loader when the app is ready.

(()=>{

    const fadeOutDuration = 400 // milliseconds

    //  ----------------- Create DOM elements ------------------- |
    const loader = document.createElement("div");
    loader.className = "app-loader";

    const spinner = document.createElement("div");
    spinner.className = "spinner";

    const text = document.createElement("div");
    text.className = "loader-text";
    text.textContent = "מכין את ציר הזמן...";

    const taskText = document.createElement("div");
    taskText.className = "loader-task-text";
    taskText.textContent = "טוען...";

    const progressTrack = document.createElement("div");
    progressTrack.className = "loader-progress-track";

    const progressFill = document.createElement("div");
    progressFill.className = "loader-progress-fill";

    progressTrack.appendChild(progressFill);

    loader.appendChild(spinner);
    loader.appendChild(text);
    loader.appendChild(taskText);
    loader.appendChild(progressTrack);

    // -------- Append styles and loader to the document --------- |

    function mount() {
        document.body.appendChild(loader);
    }

    if (document.body) {
        mount();
    } else {
        document.addEventListener('DOMContentLoaded', mount);
    }

    // A global function to remove the loader when the app is ready
    globalThis.removeLoader = () => {
        globalThis.dispatchEvent(new CustomEvent("applicationloaded"));
        loader.classList.add("fade-out");
        setTimeout(() => {
            loader.remove();
            const loaderStyles = document.getElementById("loader-styles");
            loaderStyles.remove();
        }, fadeOutDuration);
    }

    // Sets the current task label shown below the main loader text
    globalThis.setLoaderTask = (label) => {
        taskText.textContent = label ?? "";
    }

    // Sets the progress bar fill; value should be in [0, 1]
    globalThis.setLoaderProgress = (value) => {
        progressFill.style.width = `${Math.max(0, Math.min(1, value)) * 100}%`;
    }

    // A global function to show an error on the loading screen
    globalThis.loadingFailed = (error, message) => {
        spinner.remove();
        text.remove();

        const title = document.createElement("div");
        title.className = "loader-text loader-error-title";
        title.textContent = "Failed to load timeline";

        const msg = document.createElement("div");
        msg.className = "loader-error-message";
        msg.textContent = message;

        loader.appendChild(title);
        loader.appendChild(msg);

        if (error) {
            const lines = [];
            const collect = (err, prefix = "") => {
                if (!(err instanceof Error)) {
                    lines.push(prefix + String(err));
                    return;
                }
                lines.push(prefix + err.name + ": " + err.message);
                if (err.stack) {
                    // stack usually includes the message line — skip it to avoid duplication
                    const stackLines = err.stack.split("\n").filter(l => !l.startsWith(err.name + ":"));
                    lines.push(...stackLines);
                }
                if (err.cause) {
                    lines.push("", "Caused by:");
                    collect(err.cause, "  ");
                }
            };
            collect(error);

            const detail = document.createElement("div");
            detail.className = "loader-error-detail";
            detail.textContent = lines.join("\n");
            loader.appendChild(detail);
        }
    }

    // -------- Global error handlers --------- |
    globalThis.addEventListener('error', (e) => {
        loadingFailed(e.error, "An unexpected error occurred.");
    });

    globalThis.addEventListener('unhandledrejection', (e) => {
        loadingFailed(e.reason, "An unexpected error occurred.");
    });

})();