import { useEffect, useState } from 'react';
import useAxios from '../utils/useAxios'; // Assuming useAxios handles token inclusion

import imageData from '/home/mbashenko/Desktop/final/backend/media/generated/uniform.jpg';
import imageData2 from '/home/mbashenko/Desktop/final/backend/media/generated/uniform2.jpg';

const ColorCubes = ({ colorData }) => {
    return (
      <div className="color-cubes-container">
        {colorData.map((imageInfo, index) => (
          <div key={Math.random()}
          className="image-container">
            <p>Filename: {imageInfo.filename}</p>
            <div className="cube-container">
              {imageInfo.colors.map((color, colorIndex) => (
                <div
                  key={Math.random()}
                  className="color-cube"
                  style={{ backgroundColor: `rgb(${color[0]}, ${color[1]}, ${color[2]})` }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const ColorMain = ({ colorData }) => {
    return (
      <div className="color-cubes-container">
        {colorData.map((color, index) => (
                <div
                  key={index}
                  className="color-cube2"
                  style={{ backgroundColor: `rgb(${color[0]}, ${color[1]}, ${color[2]})` }}
                />
        ))}
      </div>
    );
  };

const Private = () => {
    const [res, setRes] = useState('');
    const [postRes, setPostRes] = useState('');
    const [postResColor, setPostResColor] = useState([]);
    const [mainResColor, setMainResColor] = useState([]);
    const [work, setWork] = useState(false);


    const api = useAxios();
    const [images, setImages] = useState([]); // State to store selected images

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('/test/');
                setRes(response.data.response);
            } catch (error) {
                setPostRes(error.response.data);
            }
        };
        fetchData();
    }, []);
    const handleSubmitText = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/test/', {
                text: e.target[0].value,
            });
            setPostRes(response.data.response);
        } catch (error) {
            setPostRes(error.response.data);
        }
    };
    const handleSubmitImage = async (e) => {
        e.preventDefault();
        const formData = new FormData(); // Use FormData for multipart file uploads
        setWork(false)

        try {
            for (const image of images) {
                formData.append('images', image); // Add each image to FormData
            }
            // formData.append('text', e.target[0].value); // Add text data

            const response = await api.post('/upload-images/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data', // Set content type for multipart data
                },
            });
            console.log(response.data)
            setPostRes(response.data.response);
            setPostResColor(response.data.color_data)
            setMainResColor(response.data.common_color_data)
            setImages([]); // Clear images after successful upload
            setWork(true)

        } catch (error) {
            setPostRes(error.response.data);
        }
    };

    const handleImageChange = (event) => {
        const newImages = Array.from(event.target.files); // Convert FileList to array
        setImages((prevImages) => [...prevImages, ...newImages]); // Update images state
    };

    return (
        <section>
            <h1>Private</h1>
            <p>{res}</p>
{
    work && <>
            <img src={imageData} />
            <img src={imageData2} />

    </>
}
    
            <form method="POST" onSubmit={handleSubmitImage}>
                <input
                    type="file"
                    multiple
                    onChange={handleImageChange}
                    accept="image/*" // Restrict file selection to images
                />
                <button type="submit">Submit</button>
            </form>
            <form method="POST" onSubmit={handleSubmitText}>
                <input type="text" placeholder="Enter Text" />
                <button type="submit">Submit</button>
            </form>
            {postRes && <p>{postRes}</p>}
            {postResColor && <>
                <ColorCubes colorData={postResColor} />
            </>}

            {mainResColor && <>
                <ColorMain colorData={mainResColor} />
            </>}
            
            
            {images.length > 0 && ( // Conditionally render image previews
                <div>
                    <h4>Selected Images:</h4>
                    {images.map((image) => (
                        <img key={image.name} src={URL.createObjectURL(image)} alt={image.name} /> // Display image previews
                    ))}
                </div>
            )}
        </section>
    );
};

export default Private;