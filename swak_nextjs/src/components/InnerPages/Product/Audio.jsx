"use client";
import React, { useState } from "react";

function Single() {
  const [audio, setAudio] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudio(URL.createObjectURL(file)); // preview
      setAudioFile(file); // actual file for upload
    }
  };

  const handleClick = async () => {
    try {
      if (!audioFile) {
        alert("Please upload an MP3 file first");
        return;
      }

      setLoading(true);

      const formData = new FormData();
      formData.append("file", audioFile);

      const res = await fetch("/api/your-endpoint", {
        method: "POST",
        body: formData,
      });

      // assuming API returns processed audio (blob)
      const blob = await res.blob();
      const newAudioUrl = URL.createObjectURL(blob);

      // replace audio with API result
      setAudio(newAudioUrl);

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

            {/* Audio Upload */}
            <div className="col-lg-5">
              <div className="product-img mb-4 mb-lg-0">
                <div onClick={() => document.getElementById("fileInput").click()}>
                  <input
                    id="fileInput"
                    type="file"
                    accept="audio/mpeg"
                    style={{ display: "none" }}
                    onChange={handleChange}
                  />

                  {audio ? (
                    <audio controls style={{ width: "100%" }}>
                      <source src={audio} type="audio/mpeg" />
                      Your browser does not support the audio element.
                    </audio>
                  ) : (
                    <div
                      style={{
                        width: "640px",
                        height: "200px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        border: "2px dashed #ccc",
                        borderRadius: "8px",
                        cursor: "pointer"
                      }}
                    >
                      Click to upload MP3
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Info + Button */}
            <div className="col-lg-6 offset-lg-1">
              <div className="product-info">
                <h3 className="fsz-26 fw-bold text-capitalize mb-30">
                  Audio Processing (MP3)
                </h3>

                <div className="text fsz-16 color-777 mb-30">
                  Upload an MP3 file and process it via the API.
                </div>

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
                  {loading ? "Processing..." : "Run Processing"}
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