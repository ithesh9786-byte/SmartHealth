self.addEventListener("install", (event) => {
    console.log("SmartHealth Service Worker Installed");
});

self.addEventListener("activate", (event) => {
    console.log("SmartHealth Service Worker Activated");
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return new Response("SmartHealth is offline");
        })
    );
});