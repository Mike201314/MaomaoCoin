export default function Layout(props) {
    return (
        <div className={"flex flex-col gap-3 items-center p-7"}>
            {props.children}
        </div>
    );
}



