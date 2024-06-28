
// // // Biến lưu trữ dữ liệu từ tất cả các chuyến xe
// // let allBusses = [];

// // // Hàm lấy dữ liệu từ một trang chuyến xe và thêm vào biến allBusses
// // const getBussesFromPage = async (pageUrl) => {
// //     try {
// //         let response = await fetch(pageUrl);
// //         if (!response.ok) {
// //             throw new Error('Something went wrong with status code: ' + response.status);
// //         }
// //         let data = await response.json();
// //         allBusses = allBusses.concat(data.results); // Thêm dữ liệu từ trang mới vào biến allBusses
// //         return data.next; // Trả về URL của trang kế tiếp nếu có, null nếu không
// //     } catch (error) {
// //         console.error('>>> Error:', error.message);
// //         return null;
// //     }
// };

// // // Hàm hiển thị tất cả các chuyến xe trên giao diện người dùng
// // const displayAllBusses = async () => {
// //     allBusses = []; // Reset mảng allBusses
// //     let pageUrl = 'http://127.0.0.1:8000/buss/';
// //     let nextPage = pageUrl;
// //     while (nextPage !== null) {
// //         nextPage = await getBussesFromPage(nextPage);
// //     }
// //     // Hiển thị tất cả các chuyến xe đã lấy được
// //     let busList = document.getElementById('busList');
// //     busList.innerHTML = ''; // Xóa nội dung cũ
// //     allBusses.forEach(bus => {
// //         let li = document.createElement('li');
// //         li.textContent = `ID: ${bus.id}, Name: ${bus.name}, Price: ${bus.price}`;
// //         busList.appendChild(li);
// //     });
// // };


// // Hàm lấy dữ liệu từ API backend
// const fetchDataFromBackend = async () => {
//     try {
//         const response = await fetch('http://127.0.0.1:8000/buss/');
//         if (!response.ok) {
//             throw new Error('Something went wrong');
//         }
//         const data = await response.json();
//         displayData(data); // Gọi hàm hiển thị dữ liệu khi nhận được từ API
//     } catch (error) {
//         console.error('Error:', error.message);
//     }
// };

// // Hàm hiển thị dữ liệu trên giao diện người dùng
// const displayData = (data) => {
//     let busList = document.getElementById('busList');
//     busList.innerHTML = ''; // Xóa nội dung cũ
//     data.forEach(bus => {
//         let li = document.createElement('li');
//         li.textContent = `ID: ${bus.id}, Name: ${bus.name}, Price: ${bus.price}`;
//         busList.appendChild(li);
//     });
// };

// // Gọi hàm lấy dữ liệu từ API backend khi trang được tải
// fetchDataFromBackend();
