import { useEffect, useState } from 'react';
import useAxios from '../utils/useAxios'; // Assuming useAxios handles token inclusion
import { Form, InputGroup, Row, Button } from 'react-bootstrap';
import { useAuthStore } from '../store/auth';


const List = () => {
   const [isLoggedIn, user] = useAuthStore((state) => [
      state.isLoggedIn,
      state.user,
  ]);
   const api = useAxios();
   const [ordersList, setOrdersList] = useState([])
   const [products, setProducts] = useState([])

   useEffect(() => {
      const fetchData = async () => {
          try {
              const response = await api.get('/get-list-data'); // Replace with your actual endpoint
              
              const metaData = JSON.parse(response.data.orders)
              const productsMetaData = JSON.parse(response.data.products)
                console.log(productsMetaData)
              setOrdersList(metaData)
              setProducts(productsMetaData)
          } catch (error) {
              console.error( error);
          }
      };
  
      fetchData();
  }, []);

  const deleteOrder = async (id) => {
   const deleteData = new FormData(); // Use FormData for multipart file uploads
   deleteData.append('deleteData', JSON.stringify({id})); // Add each image to FormData
   const response = await api.post('/delete-order/', deleteData, {
       headers: {
           'Content-Type': 'multipart/form-data', // Set content type for multipart data
       },
   });
   const metaData = JSON.parse(response.data)
   console.log(metaData)
   setOrdersList(metaData)
  }

  const setNewStatus = async ({pk, value}) => {
   const statusData = new FormData(); // Use FormData for multipart file uploads
   statusData.append('statusData', JSON.stringify({id: pk, value})); // Add each image to FormData
   const response = await api.post('/update-status-order/', statusData, {
       headers: {
           'Content-Type': 'multipart/form-data', // Set content type for multipart data
       },
   });
   const metaData = JSON.parse(response.data)
   setOrdersList(metaData)
  }
   return(
        <div className='orders-list'>
            {ordersList && ordersList.map((order, key) => {
               let orderData = order.fields
               return(<div className='order-child' key={Math.random()}>
                  <div className='order-child-left'>
                  <div className='order-child-title'> {orderData.title} </div>
                  <div className='order-child-cost'> {orderData.cost}$ </div>
                  </div>
                  <div className='order-child-right'>
                  {
                    (() => {
                        let productTitle = products.find(p => {
                            return p.pk === orderData.model
                        })
                        console.log(productTitle.fields.title)
                        return <div className='list-links'>
                            <a key={Math.random()} href={`http://localhost:3000/dxf?filename=${productTitle.fields.title}`} download>dxf</a>
                            <a key={Math.random()} href={`http://localhost:3000/pdf?filename=${orderData.pdfPath}`} download>pdf</a>
                            <a key={Math.random()} href={`http://localhost:3000/image?filename=${orderData.backgroundPath}`} download>bg</a>
                            <a key={Math.random()} href={`http://localhost:3000/image?filename=${orderData.cutPath}`} download>cut</a>                  
                        </div>
                    })() 
                  }
                  <Form.Group className="col col-sm-12">
                        <Form.Select className="form-control" name="size" value={orderData.status} onChange={(e) => setNewStatus({pk: order.pk, value: e.target.value})}>
                           {
                              ["DONE","SEWED", "CUT","PAINTED","CREATED"].map((o) => <option key={Math.random()} value={o}>{o}</option>)// .map((o) => <option key={Math.random()} value={o.value}>{o.value}</option>)
                           }
                        </Form.Select>
                  </Form.Group> 
                  <a className='btn btn-info' href={`/analyze?id=${order.pk}`}>ANALYZE</a>
                
                  <a className='btn btn-success' href={`/order?id=${order.pk}`}>LOOKIN</a>
            {user().user_id === orderData.creator &&
                  
                  <button className='btn btn-danger' onClick={() => deleteOrder(order.pk)}>DELETE</button>
            }
                  </div>
               </div>)
            })}
        </div>
   );
};

export default List;