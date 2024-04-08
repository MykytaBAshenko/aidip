import { useEffect, useState } from 'react';
import useAxios from '../utils/useAxios'; // Assuming useAxios handles token inclusion
import 'bootstrap/dist/css/bootstrap.min.css';
import { Form, InputGroup, Row, Button } from 'react-bootstrap';

import Dropzone from 'react-dropzone';

const Create = () => {
    const [res, setRes] = useState('');
    const [postRes, setPostRes] = useState('');
    const [postResColor, setPostResColor] = useState([]);
    const [mainResColor, setMainResColor] = useState([]);
    const [work, setWork] = useState(false);
    const [cost, setCost] = useState(0);


    const api = useAxios();
    const [images, setImages] = useState([]); // State to store selected images
    const [form, setForm] = useState({
        title: '',
        description: '',
        quantity: 0,
        
      });

      const [pageData, setPageData] = useState(null);

useEffect(() => {
    const fetchData = async () => {
        try {
            const response = await api.get('/get-create-data'); // Replace with your actual endpoint
            setPageData(response.data);

            setForm({...form, model: response.data.model.options[0].value, size: response.data.size.options[0].value  })

        } catch (error) {
            console.error( error);
        }
    };

    fetchData();
}, []);
    // useEffect(() => {
    //     const fetchData = async () => {
    //         try {
    //             const response = await api.get('/test/');
    //             setRes(response.data.response);
    //         } catch (error) {
    //             setPostRes(error.response.data);
    //         }
    //     };
    //     fetchData();
    // }, []);
    const handleChange = (e) => {
        console.log(form)
        // console.log(e)

        setForm({ ...form, [e.target.name]: e.target.value });
        calculateCost()
      }

      const submitButton = (e) => {
        e.preventDefault();
        console.log(form);
        resetButton()
      }

      const resetButton = () => {
        setForm({
          title: '',
          description: '',
          quantity: 0,
          
        });
      }

    const calculateCost = () => {
        console.log(form.model)

        let cost = Number(form.quantity) * pageData.model.options.find(o => o.value == form.model).cost *pageData.size.options.find(o => o.value == form.size).indexMult
        setCost(cost)

    }
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
    const deleteImage = (imageName) => {
        setImages(images.filter(image => image !== imageName))
    }
    const handleSubmitImage = async (e) => {
        if(e) 
        e.preventDefault();
        const formData = new FormData(); // Use FormData for multipart file uploads
        setWork(false)

        try {
            for (const image of images) {
                formData.append('images', image); // Add each image to FormData
            }
            // formData.append('text', e.target[0].value); // Add text data
            console.log(formData)
            const response = await api.post('/create-order/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data', // Set content type for multipart data
                },
            });
            console.log(response.data)
            setPostRes(response.data.response);
            setPostResColor(response.data.color_data)
            setMainResColor(response.data.common_color_data)
            // setImages([]); // Clear images after successful upload
            setWork(true)

        } catch (error) {
            console.log(error)
        }
    };

    const handleImageChange = (event) => {
        const newImages = Array.from(event); // Convert FileList to array
        setImages((prevImages) => [...prevImages, ...newImages]); // Update images state
    };

    return (
        <section>
            {/* <h1>Create order</h1>
            <p>{res}</p> */}

    
            {/* <form method="POST" onSubmit={handleSubmitImage}>
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
            )} */}
            <h1 className='pageTitle'>Create your AI outfit</h1>
            <div className='createOrderSplit'>

            <form onSubmit={(e) => submitButton(e)}  className="container mt-3 mb-3">
    <Row className="mb-3 edit-table">
        <Form.Group  className="col col-sm-12">
            <Form.Label>Title</Form.Label>
            <Form.Control type="name" name="title" value={form.name} onChange={(e) => handleChange(e)} className="form-control" />
        </Form.Group>
        <Form.Group  className="col col-sm-12">
            <Form.Label>Description</Form.Label>
            <Form.Control as="textarea" rows={3} className="form-control" name="description" value={form.description} onChange={(e) => handleChange(e)} />
        </Form.Group>
        <Form.Group  className="col col-sm-12">
            <Form.Label>Quantity</Form.Label>
            <Form.Control type="name" name="quantity" value={form.quantity} onChange={(e) => handleChange(e)} className="form-control" />
        </Form.Group>
        {pageData ? <Form.Group className="col col-sm-12">
            <Form.Label>Size</Form.Label>
            <Form.Select className="form-control" name="size" value={form.size} onChange={(e) => handleChange(e)}>
                {
                    pageData.size.options.map((o) => <option key={Math.random()} value={o.value}>{o.value}</option>)
                }
            </Form.Select>
        </Form.Group> : null}

        {pageData ? <Form.Group className="col col-sm-12">
            <Form.Label>Model</Form.Label>
            <Form.Select className="form-control" name="model" value={form.model} onChange={(e) => handleChange(e)}>
                {
                    pageData.model.options.map((o) => <option key={Math.random()} value={o.value}>{o.value}</option>)
                }
            </Form.Select>
        </Form.Group> : null}
        <Form.Group className="cost col col-sm-12">
        Cost: {cost}$
        </Form.Group>

        <Form.Group  className=" button-control col col-sm-12">
            <button type="submit" onClick={() => handleSubmitImage()} className="btn btn-info btn-lg btn-block">Generate</button>
            <button type="submit" className="btn btn-success btn-lg btn-block">Submit</button>
            <button type="reset" onClick={() => resetButton()} className="btn btn-danger btn-lg btn-block">Cancel</button>
        </Form.Group>
    <Dropzone
                    onDrop={handleImageChange}
                    multiple={true}
                    maxSize={8 * 1024 * 1024}
                >
                    {({ getRootProps, getInputProps }) => (
                        <div className="dropzone"
                            {...getRootProps()}
                        >
                            <input {...getInputProps()} />
<div className='Dropzoneeee' >
    Put your env images here images here.
</div>

                        </div>
                    )}

                </Dropzone>
                {images.length > 0 && ( // Conditionally render image previews
                <div className='images-list'>
                    <h4>Selected Images:</h4>
                    <div className='images-list-list'>

                    {images.map((image, i) => (
                        <img key={i} onClick={() => deleteImage(image)} src={URL.createObjectURL(image)} alt={image.name} /> // Display image previews
                    ))}
                </div>
                </div>
            )}
    </Row>

</form>

</div>
{/* <form method="POST" onSubmit={handleSubmitImage}>
                <input
                    type="file"
                    multiple
                    onChange={handleImageChange}
                    accept="image/*" // Restrict file selection to images
                />
                <button type="submit">Submit</button>
            </form> */}
            <div className="new-task-photo-control">
                {/* {photos.map((img, i) => <div key={i} onClick={() => dropImage(i)} className="new-task-photo-control-shell"><img src={img} /></div>)} */}


            </div>
            {/* <form method="POST" onSubmit={handleSubmitText}>
                <button type="submit">Submit</button>
            </form> */}
            {/* {postRes && <p>{postRes}</p>} */}
            {/* {postResColor && <>
                <ColorCubes colorData={postResColor} />
            </>}

            {mainResColor && <>
                <ColorMain colorData={mainResColor} />
            </>} */}
            
            

        </section>
    );
};

export default Create;