import Layout from "./Layout";
import {useEffect, useState} from "react";

export default function App() {
    return (
        <Layout>
            <h1 className={"text-3xl font-bold"}>Hello, this is your MaomaoCoin GUI</h1>

            <Section title={"Wallet"}>1</Section>
            <Section title={"Online Peers"}>
                <Peers/>
            </Section>
        </Layout>
    );
}


function Section({children,title}) {
  return (
      <div className={"flex flex-col border-2 rounded-xl shadow-md backdrop-blur-xl gap-3 w-full max-w-[1200px] m-3 p-7"}>
          <h1 className={"font-bold text-3xl"}>{title}</h1>
          <div className={""}>
              {children}
          </div>

      </div>
  );
}

function Peers(){

    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    const baseURL = window.location.origin;
    const req_URL = baseURL + "/getActivePeers";

    const fetchData = () => {
        setLoading(true)
        fetch(req_URL)
            .then(response => response.json())
            .then(data => setData(data));
        setLoading(false)
    }

    useEffect(fetchData, []);

    return (
        <>
            {loading ? (
                <div className={"flex flex-col gap-3 items-center"}>
                    <h1 className={"font-bold text-2xl"}>Loading...</h1>
                </div>
            ) : (
                <div className={"flex flex-col gap-3"}>
                    <button onClick={fetchData} className={"border-2 w-fit p-1.5 rounded-3xl"}>Refresh</button>
                    <div className={"flex flex-col gap-3 w-full"}>
                        {data.map((peer) => (
                            <div className={"border-b-2"}>
                                <h1 className={"font-medium"}>{peer}</h1>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </>
    );
}
