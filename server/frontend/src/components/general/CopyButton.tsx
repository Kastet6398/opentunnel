import React from "react";
import { ClipboardDocumentIcon } from "@heroicons/react/24/outline";
import { Bounce, toast, ToastContainer } from "react-toastify";

interface CopyButtonProps {
  text: string;
}

export const CopyButton: React.FC<CopyButtonProps> = ({ text }) => {
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast("Copied to clipboard!", { type: "success" });
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };
  return (
    <>
      <button
        onClick={() => copyToClipboard(text)}
        className="p-2 text-gray-500 hover:text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
        title="Copy token to clipboard"
      >
        <ClipboardDocumentIcon className="h-4 w-4" />
      </button>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        pauseOnFocusLoss
        draggable
        transition={Bounce}
        className="select-none"
      />
    </>
  );
};
