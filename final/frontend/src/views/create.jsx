import { useEffect, useState } from 'react';
import useAxios from '../utils/useAxios'; // Assuming useAxios handles token inclusion
import 'bootstrap/dist/css/bootstrap.min.css';
import { Form, InputGroup, Row, Button } from 'react-bootstrap';

import Dropzone from 'react-dropzone';

const Create = () => {

    const [cost, setCost] = useState(0);
    const [generated, setGenerated] = useState(false);
    const [generatedWithCut, setGeneratedWithCut] = useState(false);
    const [pdf, setPdf] = useState(false);
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
            const metaData = JSON.parse(response.data)
            // console.log(metaData)
            metaData.map((md) => {
                md.fields.sizeArray = JSON.parse(md.fields.sizeArray.replace(/'/g, '"'))
            })
            // JSON.parse(stringData.replace(/'/g, '"'))
            setPageData(metaData)
            setForm({...form, model: metaData[0].fields.title, size: metaData[0].fields.sizeArray[0]  })

        } catch (error) {
            console.error( error);
        }
    };

    fetchData();
}, []);

    const getNeededDataObject = (title) => {
        return pageData.find(o => o.fields.title === title).fields
    }

    const handleChange = (e) => {
        setForm(prevForm => ({
            ...prevForm,
            [e.target.name]: e.target.value
          }));
          
          // Now, let's use the updated form
          if(e.target.name === "quantity")
          {           let cost = Number(e.target.value) * pageData.find(o => o.fields.title === form.model).fields.cost;
          setCost(cost);
      }}

      const submitButton = (e) => {
        e.preventDefault();
        console.log(form);
        // resetButton()
      }


    const deleteImage = (imageName) => {
        setImages(images.filter(image => image !== imageName))
    }
    const handleSubmitImage = async (e) => {
        if(e) 
        e.preventDefault();
        const formData = new FormData(); // Use FormData for multipart file uploads
        try {
            for (const image of images) {
                formData.append('images', image); // Add each image to FormData
            }
            formData.append('formData', JSON.stringify({...form, cost})); // Add each image to FormData

            const response = await api.post('/generate-order/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data', // Set content type for multipart data
                },
            });
            setGenerated(response.data.generated_filename)
            setGeneratedWithCut(response.data.generated_with_cut_filename)
            setPdf(response.data.generated_pdf_filename)
        } catch (error) {
            console.log(error)
        }
    };

    const createOrder =  async (e) => {
        if(e) 
        e.preventDefault();
        const formData = new FormData(); // Use FormData for multipart file uploads
        try {

            formData.append('formData', JSON.stringify({...form, pdf, cost, generated, generatedWithCut})); // Add each image to FormData
            const response = await api.post('/create-order/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data', // Set content type for multipart data
                },
            });
            console.log(response.data)
            alert(response.data.response);
            window.location.href = "/list";
        } catch (error) {
            console.log(error)
        }
    }

    const handleImageChange = (event) => {
        const newImages = Array.from(event); // Convert FileList to array
        setImages((prevImages) => [...prevImages, ...newImages]); // Update images state
    };

    return (
        <section>
            <h1 className='pageTitle'>Create your AI outfit</h1>
            <div className='createOrderSplit'>

            <form onSubmit={(e) => submitButton(e)}  className="container mt-3 mb-3">
    <Row className="mb-3 edit-table">
        <Form.Group  className="col col-sm-12">
            <Form.Label>Title</Form.Label>
            <Form.Control type="name" name="title" value={form.title} onChange={(e) => handleChange(e)} className="form-control" />
        </Form.Group>
        <Form.Group  className="col col-sm-12">
            <Form.Label>Description</Form.Label>
            <Form.Control as="textarea" rows={3} className="form-control" name="description" value={form.description} onChange={(e) => handleChange(e)} />
        </Form.Group>
        <Form.Group  className="col col-sm-12">
            <Form.Label>Quantity</Form.Label>
            <Form.Control type="name" name="quantity" value={form.quantity} onChange={(e) => handleChange(e)} className="form-control" />
        </Form.Group>
        {pageData && form.model ? <Form.Group className="col col-sm-12">
            <Form.Label>Size</Form.Label>
            <Form.Select className="form-control" name="size" value={form.size} onChange={(e) => handleChange(e)}>
                {
                    getNeededDataObject(form.model).sizeArray.map((o) => <option key={Math.random()} value={o}>{o}</option>)// .map((o) => <option key={Math.random()} value={o.value}>{o.value}</option>)
                }
            </Form.Select>
        </Form.Group> : null}

        {pageData ? <Form.Group className="col col-sm-12">
            <Form.Label>Model</Form.Label>
            <Form.Select className="form-control" name="model" value={form.model} onChange={(e) => handleChange(e)}>
                {
                    pageData.map((o) => <option key={Math.random()} value={o.fields.title}>{o.fields.title}</option>)
                }
            </Form.Select>
        </Form.Group> : null}
        <Form.Group className="cost col col-sm-12">
        Cost: {cost}$
        </Form.Group>

        <Form.Group  className=" button-control col col-sm-12">
            <button type="submit" onClick={() => handleSubmitImage()} className="btn btn-info btn-lg btn-block">Generate</button>
            <button type="submit" onClick={() => createOrder()}  className="btn btn-success btn-lg btn-block">Create</button>
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
<div className='generated_images'>
{pdf ? <a href={`http://localhost:3000/pdf?filename=${pdf}`} target='blank'>Generated PDF for this order</a>: null}

    {
        generated ? <div> Generated background </div> : null
    }
{generated ? <img src={`http://localhost:3000/image?filename=${generated}`}></img> : null}
{
        generatedWithCut ? <div> Generated background with cut</div> : null
    }
{generatedWithCut ? <img src={`http://localhost:3000/image?filename=${generatedWithCut}`}></img> : null}
</div>
</div>
        </section>
    );
};

export default Create;