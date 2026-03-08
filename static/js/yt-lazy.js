document.addEventListener("DOMContentLoaded", function() {
    var lazyVideos = [].slice.call(document.querySelectorAll(".yt-lazy"));
    var lazyPlaylists = [].slice.call(document.querySelectorAll(".yt-playlist-lazy"));

    if ("IntersectionObserver" in window) {
        var lazyVideoObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(video) {
                if (video.isIntersecting) {
                    var el = video.target;
                    var ytid = el.getAttribute('data-ytid');
                    if (ytid) {
                        // Use maxresdefault for high quality thumbnail
                        var thumb = "https://img.youtube.com/vi/" + ytid + "/maxresdefault.jpg";
                        el.style.backgroundImage = "url('" + thumb + "')";
                        el.style.backgroundSize = "cover";
                        el.style.backgroundPosition = "center";
                        el.style.cursor = "pointer"; // Make whole area clickable
                        el.innerHTML = '<div class="play-button" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 68px; height: 48px; background-color: rgba(255, 0, 0, 0.8); border-radius: 12px; display: flex; align-items: center; justify-content: center; pointer-events: none;"><svg height="24px" width="24px" version="1.1" viewBox="0 0 24 24"><path d="M8,5v14l11-7L8,5z" fill="#fff"></path></svg></div>';
                        
                        // Add click listener to the whole container
                        el.addEventListener('click', function() {
                            // Open YouTube video in new tab instead of embedding
                            window.open('https://www.youtube.com/watch?v=' + ytid, '_blank');
                            
                            // DO NOT replace innerHTML with iframe to prevent playback error
                            // Just keep the thumbnail visible
                        });
                    }
                    lazyVideoObserver.unobserve(el);
                }
            });
        });

        lazyVideos.forEach(function(lazyVideo) {
            lazyVideoObserver.observe(lazyVideo);
        });
        
        // Handle Playlists
        var lazyPlaylistObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(playlist) {
                if (playlist.isIntersecting) {
                    var el = playlist.target;
                    var listid = el.getAttribute('data-listid');
                    if (listid) {
                        // For playlists, we can't easily get a thumbnail without API key, 
                        // so we might just load it or show a generic placeholder.
                        // Here we just load it directly when in view to save initial page load.
                        el.innerHTML = '<iframe src="https://www.youtube.com/embed/videoseries?list=' + listid + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="width: 100%; height: 100%;"></iframe>';
                    }
                    lazyPlaylistObserver.unobserve(el);
                }
            });
        });
        
        lazyPlaylists.forEach(function(lazyPlaylist) {
            lazyPlaylistObserver.observe(lazyPlaylist);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        lazyVideos.forEach(function(el) {
             var ytid = el.getAttribute('data-ytid');
             if (ytid) {
                 el.innerHTML = '<iframe src="https://www.youtube.com/embed/' + ytid + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="width: 100%; height: 100%;"></iframe>';
             }
        });
        lazyPlaylists.forEach(function(el) {
             var listid = el.getAttribute('data-listid');
             if (listid) {
                 el.innerHTML = '<iframe src="https://www.youtube.com/embed/videoseries?list=' + listid + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="width: 100%; height: 100%;"></iframe>';
             }
        });
    }
});
