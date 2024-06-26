import { useEffect, useState } from 'react';
import useAxios from '../utils/useAxios'; // Assuming useAxios handles token inclusion
import 'bootstrap/dist/css/bootstrap.min.css';
import { Form, InputGroup, Row, Button } from 'react-bootstrap';
import { useAuthStore } from '../store/auth';

import Dropzone from 'react-dropzone';

const Analyze = () => {
    const [isLoggedIn, user] = useAuthStore((state) => [
        state.isLoggedIn,
        state.user,
    ]);
    const [generated_background, setGenerated_background] = useState(false);
    const [generated_red_background, setGenerated_red_background] = useState(false);
    const [csv_long, setCsv_long] = useState(false);
    const [csv_matrix, setCsv_matrix] = useState(false);
    const [difference, setDifference] = useState(false);
    const [generated, setGenerated] = useState(false);
    const [fix_background, setFix_background] = useState(false);


    
    
    const api = useAxios();
    const [images, setImages] = useState([]); // State to store selected images
    const [form, setForm] = useState({
        fromX: 0,
        fromY: 0,
        width: 100,
        height: 100,
        
      });


useEffect(() => {
    const fetchData = async () => {
        try {
           

            const formData = new FormData(); // Use FormData for multipart file uploads
            try {
                const urlParams = new URLSearchParams(window.location.search);
                formData.append('updateData', JSON.stringify({id: urlParams.get('id')})); // Add each image to FormData
                const response = await api.post('/get-analyze-order/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data', // Set content type for multipart data
                    },
                });
                console.log(JSON.parse(response.data)[0].fields)
                let form = JSON.parse(response.data)[0].fields
                setGenerated(form.backgroundPath)

            } catch (error) {
                console.log(error)
            }

            user()
        } catch (error) {
            console.error( error);
        }
    };

    fetchData();
}, []);


    const handleChange = (e) => {
        setForm(prevForm => ({
            ...prevForm,
            [e.target.name]: e.target.value
          }));
          
       }

      const submitButton = (e) => {
        e.preventDefault();
        console.log(form);
        // resetButton()
      }


    const deleteImage = (imageName) => {
        setImages(images.filter(image => image !== imageName))
    }
    const analyzeImage = async (e) => {
        if(e) 
        e.preventDefault();
        const formData = new FormData(); // Use FormData for multipart file uploads
        try {
            for (const image of images) {
                formData.append('images', image); // Add each image to FormData
            }
            formData.append('formData', JSON.stringify({...form, generated})); // Add each image to FormData

            console.log(formData)
            const response = await api.post('/analyze/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data', // Set content type for multipart data
                },
            });
            console.log(response.data)
            setGenerated_background(response.data.generated_background)
            setGenerated_red_background(response.data.generated_red_background)
            setCsv_long(response.data.csv_long)
            setCsv_matrix(response.data.csv_matrix)
            setDifference(response.data.difference
            )
            setFix_background(response.data.fix_background)

            // setGenerated(response.data.generated_filename)
        } catch (error) {
            console.log(error)
        }
    };

    const handleImageChange = (event) => {
        const newImages = Array.from(event); // Convert FileList to array
        setImages(() => [newImages[0]]); // Update images state
    };

    return (
        <section>
            <h1 className='pageTitle'>Analyze drawing images</h1>
            <div className='createOrderSplit'>

            <form onSubmit={(e) => submitButton(e)}  className="container mt-3 mb-3">
    <Row className="mb-3 edit-table">
        <Form.Group  className="col col-sm-12">
            <Form.Label>from X %</Form.Label>
            <Form.Control type="number" name="fromX" value={form.fromX} onChange={(e) => handleChange(e)} className="form-control" />
        </Form.Group>
        <Form.Group  className="col col-sm-12">
            <Form.Label>from Y %</Form.Label>
            <Form.Control type="number" className="form-control" name="fromY" value={form.fromY} onChange={(e) => handleChange(e)} />
        </Form.Group>
        <Form.Group  className="col col-sm-12">
            <Form.Label>Width</Form.Label>
            <Form.Control type="number" name="width" value={form.width} onChange={(e) => handleChange(e)} className="form-control" />
        </Form.Group>
        <Form.Group  className="col col-sm-12">
            <Form.Label>Height</Form.Label>
            <Form.Control type="number" name="height" value={form.height} onChange={(e) => handleChange(e)} className="form-control" />
        </Form.Group>

        <Form.Group  className=" col col-sm-12">
        
            <button type="submit" onClick={() => analyzeImage()}  className="btn anal btn-success btn-lg btn-block">ANALYZE</button>
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
    Put your painted image here images here.
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

        {/* {generated_background ? <a href={`http://localhost:3000/analyze/image?filename=${generated_background}`} target='blank'>Generated background for order</a>: null} */}
        <div className='gen_links'>
            {fix_background ? <a href={`http://localhost:3000/analyze/image?filename=${fix_background}`} target='blank'>FIXED PATTERN</a>: null}
            {generated_red_background ? <a href={`http://localhost:3000/analyze/image?filename=${generated_red_background}`} target='blank'>Generated background with red difference for order</a>: null}
            {csv_long ? <a href={`http://localhost:3000/analyze/csv?filename=${csv_long}`} target='blank'>CSV pixel data</a>: null}
            {csv_matrix ? <a href={`http://localhost:3000/analyze/csv?filename=${csv_matrix}`} target='blank'>CSV matrix</a>: null}
        </div>
        {difference !== false ? 
            (difference < 1) ? 
            <div className='genLime'>{difference}</div> :<div className='genERRROR'>{difference}</div>: null}

                {
                    generated ? <div> Generated background </div> : null
                }
            {generated ? <img src={`http://localhost:3000/image?filename=${generated}`}></img> : null}
                 </div>
        </div>
        </section>
    );
};

export default Analyze;