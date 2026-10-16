using UnityEngine;

namespace CGVR.Exp9
{
    // A coin with a trigger collider: when the player walks into it, the score goes up and the coin disappears
    public class Collectible : MonoBehaviour
    {
        void OnTriggerEnter(Collider other)
        {
            if (other.GetComponent<PlayerController>() == null)
            {
                return;
            }

            LabGame game = GetComponentInParent<LabGame>();

            if (game != null)
            {
                game.CollectCoin();
            }

            gameObject.SetActive(false);
        }
    }
}
