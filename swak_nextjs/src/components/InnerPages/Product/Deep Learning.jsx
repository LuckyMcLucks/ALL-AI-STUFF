"use client";
import React, { useState } from "react";

function Single() {
  const [text, setText] = useState("");
  const [followers, setFollowers] = useState("");
  const [retweets, setRetweets] = useState("");
  const [favourites, setFavourites] = useState("");
  const [likes, setLikes] = useState("");
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    try {
      if (!text) {
        alert("Please enter tweet text");
        return;
      }

      setLoading(true);

      const res = await fetch("/api/your-endpoint", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          followers,
          retweets,
          favourites,
          likes,
        }),
      });

      const data = await res.json();
      console.log(data); // handle result later

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="tc-product-single-style1">
      <div className="main-info mb-100">
        <div className="container">
          <div className="row gx-0">

            <div className="col-lg-6 offset-lg-1">
              <div className="product-info">

                <h3 className="fsz-26 fw-bold text-capitalize mb-30">
                  Deep Learning Bot Tweet Classifier
                </h3>

                {/* Tweet Text */}
                <label>Tweet</label>
<textarea
  value={text}
  onChange={(e) => setText(e.target.value)}
  placeholder="Enter your tweet here..."
  rows={4}
  style={{
    display: "block",
    width: "100%",
    minHeight: "120px",
    resize: "vertical", // user can drag to expand
    padding: "10px",
    marginBottom: "15px",
    borderRadius: "6px",
    border: "1px solid #ccc"
  }}
/>

                {/* Followers */}
                <label>Followers</label>
                <input
                  type="number"
                  value={followers}
                  onChange={(e) => setFollowers(e.target.value)}
                  placeholder="Number of followers"
                  style={{ display: "block", width: "100%", marginBottom: "15px" }}
                />

                {/* Retweets */}
                <label>Retweets</label>
                <input
                  type="number"
                  value={retweets}
                  onChange={(e) => setRetweets(e.target.value)}
                  placeholder="Number of retweets"
                  style={{ display: "block", width: "100%", marginBottom: "15px" }}
                />

                {/* Favourites */}
                <label>Favourites</label>
                <input
                  type="number"
                  value={favourites}
                  onChange={(e) => setFavourites(e.target.value)}
                  placeholder="Number of favourites"
                  style={{ display: "block", width: "100%", marginBottom: "15px" }}
                />

                {/* Likes */}
                <label>Likes</label>
                <input
                  type="number"
                  value={likes}
                  onChange={(e) => setLikes(e.target.value)}
                  placeholder="Number of likes"
                  style={{ display: "block", width: "100%", marginBottom: "20px" }}
                />

                <button
                  onClick={handleClick}
                  disabled={loading}
                  style={{
                    padding: "12px 24px",
                    background: "#007bff",
                    color: "#fff",
                    border: "none",
                    borderRadius: "6px",
                    cursor: "pointer"
                  }}
                >
                  {loading ? "Processing..." : "Run Detection"}
                </button>

              </div>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}

export default Single;