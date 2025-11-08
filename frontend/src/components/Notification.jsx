export default function Notification({ message, tone = "info" }) {
	if (!message) {
		return null;
	}

	return <div className={'notification ' + tone}>{message}</div>;
}